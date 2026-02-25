import arcpy
import os
projection=arcpy.SpatialReference("NAD 1983 CSRS 3TM 114")

arcpy.env.workspace = r"C:\Capstone\Working_Geodatabase" #Data path
workspace = arcpy.env.workspace
arcpy.env.overwriteOutput = True

def features(workspace):
    data = []  # Create a list

    for dirpath, dirnames, filenames in arcpy.da.Walk(workspace):
        for f in filenames:
            data_path = os.path.join(dirpath, f)
            data.append(data_path)
    return data

data_shp = features(workspace)
for data in data_shp:
     print(data)

# setting gdb
wkspaces = arcpy.ListWorkspaces("", "FileGDB")
for gdb in wkspaces:
    if arcpy.Exists(gdb):
        arcpy.management.Delete(gdb)
        print("Deleting existing gdb...")

gdb_name = "Group2_Capstone"            #GDB NAME
arcpy.management.CreateFileGDB(workspace, gdb_name + ".gdb")
gdb_path=os.path.join(workspace, gdb_name + ".gdb")
print(arcpy.GetMessages())
print("")

#Identifying study area
studyArea_symbology=r"C:\Capstone\Working_Geodatabase\Study_Area.lyrx"
sections_shp = next(p for p in data_shp if os.path.basename(p).lower() == "v4-1_sec.shp")
section_layer=arcpy.MakeFeatureLayer_management(sections_shp, "sections_layer")
delimfield=arcpy.AddFieldDelimiters(sections_shp, "DESCRIPTOR")
arcpy.SelectLayerByAttribute_management(section_layer, "NEW_SELECTION", delimfield + " = 'SEC-01 TWP-027 RGE-29 MER-4'")
studyarea_path=os.path.join(gdb_path, "Study_Area")
arcpy.management.Project("sections_layer", studyarea_path, projection)
arcpy.management.ApplySymbologyFromLayer("sections_layer", studyArea_symbology)

#clipping features to study
data = [
    "Pipelines_GCS_NAD83.shp",
    "Subsurface_Lineaments__WebM.shp",
    "glac_landform_ln_ll.shp",
    "Airdrie_Roads.shp"
]

studyarea_fc = os.path.join(gdb_path, "Study_Area")

for name in data:

    # find full path from your earlier data_shp list
    fc_path = next(p for p in data_shp if os.path.basename(p).lower() == name.lower())

    base = os.path.splitext(name)[0]

    projected_fc = os.path.join(gdb_path, base + "_prj")
    clipped_fc   = os.path.join(gdb_path, base + "_clip")

    # Project
    arcpy.management.Project(fc_path, projected_fc, projection)

    # Clip projected feature to Study Area
    arcpy.analysis.Clip(projected_fc, studyarea_fc, clipped_fc)

    arcpy.management.Delete(projected_fc)

    print(f"PROJECTED + CLIPPED: {name} -> {clipped_fc}")

