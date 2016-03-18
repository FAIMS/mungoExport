'''
Python:
    accept epsg as argument

    copy into new DB
    create structure for 3nf
    add geometry columns
    Call Ruby:
        Write responses into 3nf
    write geometries into 3nf tables

    call shapefile tool


    TODO:
        convert ruby calls into rbenv or system ruby calls
        figure out how shell script wrapper needs to work for exporter


'''

import unicodedata
import sqlite3
import csv, codecs, cStringIO
from xml.dom import minidom
import sys
import pprint
import glob
import json
import os
import shutil
import re
import zipfile
import subprocess
import glob
import tempfile
import errno
import imghdr
import bz2
import tarfile

from collections import defaultdict
import zipfile
try:
    import zlib
    compression = zipfile.ZIP_DEFLATED
except:
    compression = zipfile.ZIP_STORED

modes = { zipfile.ZIP_DEFLATED: 'deflated',
          zipfile.ZIP_STORED:   'stored',
          }

print sys.argv

class UTF8Recoder:
    """
    Iterator that reads an encoded stream and reencodes the input to UTF-8
    """
    def __init__(self, f, encoding):
        self.reader = codecs.getreader(encoding)(f)

    def __iter__(self):
        return self

    def next(self):
        return self.reader.next().encode("utf-8")

class UnicodeReader:
    """
    A CSV reader which will iterate over lines in the CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        f = UTF8Recoder(f, encoding)
        self.reader = csv.reader(f, dialect=dialect, **kwds)

    def next(self):
        row = self.reader.next()
        return [unicode(s, "utf-8") for s in row]

    def __iter__(self):
        return self

class UnicodeWriter:
    """
    A CSV writer which will write rows to CSV file "f",
    which is encoded in the given encoding.
    """

    def __init__(self, f, dialect=csv.excel, encoding="utf-8", **kwds):
        # Redirect output to a queue
        self.queue = cStringIO.StringIO()
        self.writer = csv.writer(self.queue, dialect=dialect, **kwds)
        self.stream = f
        self.encoder = codecs.getincrementalencoder(encoding)()

    def convertBuffer(self, obj):

        #print type(obj)        
        
        if isinstance(obj, basestring):         
            #print obj.encode("utf-8", errors="replace")
            return obj.encode("utf-8", errors="replace").replace('"',"''")
        if isinstance(obj, buffer):         
            bufferCon = sqlite3.connect(':memory:')
            bufferCon.enable_load_extension(True)
            bufferCon.load_extension("libspatialite.so.5")
            foo = bufferCon.execute("select astext(?);", ([obj])).fetchone()            
            return foo[0]
        if obj == None:
            return ""
        return obj



    def writerow(self, row):
        self.writer.writerow(['"%s"' % self.convertBuffer(s) for s in row])
        # Fetch UTF-8 output from the queue ...
        data = self.queue.getvalue()
        data = data.decode("utf-8")
        # ... and reencode it into the target encoding
        data = self.encoder.encode(data)
        # write to the target stream
        self.stream.write(data.replace('"""','"').replace('"None"',''))
        # empty queue
        self.queue.truncate(0)
        self.stream.flush()

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


    



def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d


def upper_repl(match):
    if (match.group(1) == None):
        return ""
    return match.group(1).upper()

def clean(str):
     out = re.sub(" ([a-z])|[^A-Za-z0-9]+", upper_repl, str)     
     return out

def cleanWithUnder(str):
     out = re.sub("[^a-zA-Z0-9]+", "_", str)     
     return out  

def makeSurePathExists(path):
    try:
        os.makedirs(path)
    except OSError as exception:
        if exception.errno != errno.EEXIST:
            raise


originalDir = sys.argv[1]
exportDir = tempfile.mkdtemp()+"/"
finalExportDir = sys.argv[2]+"/"
importDB = originalDir+"db.sqlite3"
exportDB = exportDir+"shape.sqlite3"
jsondata = json.load(open(originalDir+'module.settings'))
srid = jsondata['srid']
arch16nFiles=[]
for file in glob.glob(originalDir+"*.properties"):
    arch16nFiles.append(file)

arch16nFile = next((s for s in arch16nFiles if '.0.' in s), arch16nFiles[0])
# print jsondata
moduleName = clean(jsondata['name'])
fileNameType = "Identifier" #Original, Unchanged, Identifier

images = None
try:
    foo= json.load(open(sys.argv[3],"r"))
    # print foo["Export Images and Files?"]
    if (foo["Export Images and Files?"] != []):
        images = True
    else:
        images = False
except:
    sys.stderr.write("Json input failed")
    images = True

print "Exporting Images %s" % (images)

def zipdir(path, zip):
    for root, dirs, files in os.walk(path):
        for file in files:
            zip.write(os.path.join(root, file))


try:
    os.remove(exportDB)
except OSError:
    pass

importCon = sqlite3.connect(importDB)
importCon.enable_load_extension(True)
importCon.load_extension("libspatialite.so.5")
exportCon = sqlite3.connect(exportDB)
exportCon.enable_load_extension(True)
exportCon.load_extension("libspatialite.so.5")


exportCon.execute("select initSpatialMetaData(1)")
'''
for line in importCon.iterdump():
    try:
        exportCon.execute(line)
    except sqlite3.Error:       
        pass
'''     
            
exifCon = sqlite3.connect(exportDB)
exifCon.row_factory = dict_factory
exportCon.enable_load_extension(True)
exportCon.load_extension("libspatialite.so.5")


  
exportCon.execute("create table keyval (key text, val text);")

f = open(arch16nFile, 'r')
for line in f:
    if "=" in line:
        keyval = line.replace("\n","").replace("\r","").decode("utf-8").split('=')
        keyval[0] = '{'+keyval[0]+'}'
        exportCon.execute("replace into keyval(key, val) VALUES(?, ?)", keyval)
f.close()







for aenttypeid, aenttypename in importCon.execute("select aenttypeid, aenttypename from aenttype"): 
    aenttypename = clean(aenttypename)
    attributes = ['identifier', 'createdBy', 'createdAtGMT', 'modifiedBy', 'modifiedAtGMT']
    for attr in importCon.execute("select distinct attributename from attributekey join idealaent using (attributeid) where aenttypeid = ? group by attributename order by aentcountorder", [aenttypeid]):
        attrToInsert = clean(attr[0])
        if attrToInsert not in attributes:
            attributes.append(attrToInsert)
    attribList = " TEXT, \n\t".join(attributes)
    createStmt = "Create table if not exists %s (\n\tuuid TEXT PRIMARY KEY,\n\t%s TEXT);" % (aenttypename, attribList)

    exportCon.execute(createStmt)

geometryColumns = []
for row in importCon.execute("select aenttypename, geometrytype(geometryn(geospatialcolumn,1)) as geomtype, count(distinct geometrytype(geometryn(geospatialcolumn,1))) from latestnondeletedarchent join aenttype using (aenttypeid) where geomtype is not null group by aenttypename having  count(distinct geometrytype(geometryn(geospatialcolumn,1))) = 1"):
    geometryColumns.append(row[0])
    geocolumn = "select addGeometryColumn('%s', 'geospatialcolumn', %s, '%s', 'XY');" %(clean(row[0]),srid,row[1]);
    
    exportCon.execute(geocolumn)





for aenttypename, uuid, createdAt, createdBy, modifiedAt, modifiedBy,geometry in importCon.execute("select aenttypename, uuid, createdAt || ' GMT', createdBy, datetime(modifiedAt) || ' GMT', modifiedBy, geometryn(transform(geospatialcolumn,casttointeger(%s)),1) from latestnondeletedarchent join aenttype using (aenttypeid) join createdModifiedAtBy using (uuid) order by createdAt" % (srid)):
    
    if (aenttypename in geometryColumns):       
        insert = "insert into %s (uuid, createdAtGMT, createdBy, modifiedAtGMT, modifiedBy, geospatialcolumn) VALUES(?, ?, ?, ?, ?, ?)" % (clean(aenttypename))
        exportCon.execute(insert, [str(uuid), createdAt, createdBy, modifiedAt, modifiedBy, geometry])
    else:
        insert = "insert into %s (uuid, createdAtGMT, createdBy, modifiedAtGMT, modifiedBy) VALUES(?, ?, ?, ?, ?)" % (clean(aenttypename))
        exportCon.execute(insert, [str(uuid), createdAt, createdBy, modifiedAt, modifiedBy])



try:
    os.remove(exportDir+'shape.out')
except OSError:
    pass


subprocess.call(["bash", "./format.sh", originalDir, exportDir, exportDir])



updateArray = []

for line in codecs.open(exportDir+'shape.out', 'r', encoding='utf-8').readlines():  
    out = line.replace("\n","").replace("\\r","").split("\t")
    #print "!!%s -- %s!!" %(line, out)
    if (len(out) ==4):      
        update = "update %s set %s = ? where uuid = %s;" % (clean(out[1]), clean(out[2]), out[0])
        data = (unicode(out[3].replace("\\n","\n").replace("'","''")),)
        # print update, data
        exportCon.execute(update, data)




exportCon.commit()
files = ['shape.sqlite3']


if images:
    for directory in importCon.execute("select distinct aenttypename, attributename from latestnondeletedaentvalue join attributekey using (attributeid) join latestnondeletedarchent using (uuid) join aenttype using (aenttypeid) where attributeisfile is not null and measure is not null"):
        makeSurePathExists("%s/%s/%s" % (exportDir,clean(directory[0]), clean(directory[1])))

    filehash = defaultdict(int)

    exportPhotos = []
    realExportList = {}

    print "* File list exported:"
    for filename in importCon.execute("select uuid, measure, freetext, certainty, attributename, aenttypename from latestnondeletedaentvalue join attributekey using (attributeid) join latestnondeletedarchent using (uuid) join aenttype using (aenttypeid) where attributeisfile is not null and measure is not null"):
        try:        
            oldPath = filename[1].split("/")
            oldFilename = oldPath[2]
            aenttypename = clean(filename[5])
            attributename = clean(filename[4])
            newFilename = "%s/%s/%s" % (aenttypename, attributename, oldFilename)
            if os.path.isfile(originalDir+filename[1]):
                if (fileNameType == "Identifier"):
                    # print filename[0]
                    
                    filehash["%s%s" % (filename[0], attributename)] += 1
                    

                    foo = exportCon.execute("select identifier from %s where uuid = %s" % (aenttypename, filename[0]))
                    identifier=cleanWithUnder(foo.fetchone()[0])

                    r= re.search("(\.[^.]*)$",oldFilename)

                    delimiter = ""
                    
                    if filename[2]:
                        delimiter = "a"

                    newFilename =  "%s/%s/%s_%s%s%s" % (aenttypename, attributename, identifier, filehash["%s%s" % (filename[0], attributename)],delimiter, r.group(0))
                    


                exifdata = exifCon.execute("select * from %s where uuid = %s" % (aenttypename, filename[0])).fetchone()
                iddata = [] 
                for id in importCon.execute("select coalesce(measure, vocabname, freetext) from latestnondeletedarchentidentifiers where uuid = %s union select aenttypename from latestnondeletedarchent join aenttype using (aenttypeid) where uuid = %s" % (filename[0], filename[0])):
                    iddata.append(id[0])


                shutil.copyfile(originalDir+filename[1], exportDir+newFilename)

                mergedata = exifdata.copy()
                mergedata.update(jsondata)
                mergedata.pop("geospatialcolumn", None)
                exifjson = {"SourceFile":exportDir+newFilename, 
                            "UserComment": [json.dumps(mergedata)], 
                            "ImageDescription": exifdata['identifier'], 
                            "XPSubject": "Annotation: %s" % (filename[2]),
                            "Keywords": iddata,
                            "Artist": exifdata['createdBy'],
                            "XPAuthor": exifdata['createdBy'],
                            "Software": "FAIMS Project",
                            "ImageID": exifdata['uuid'],
                            "Copyright": jsondata['name']


                            }
                with open(exportDir+newFilename+".json", "w") as outfile:
                    json.dump(exifjson, outfile)    

                if imghdr.what(exportDir+newFilename):
                    
                    subprocess.call(["exiftool", "-m", "-q", "-sep", "\"; \"", "-overwrite_original", "-j=%s" % (exportDir+newFilename+".json"), exportDir+newFilename])

                exportPhotos.append((clean(aenttypename), attributename, newFilename, filename[0]))
                print "    * %s" % (newFilename)
                files.append(newFilename+".json")
                files.append(newFilename)
            else:
                print "<b>Unable to find file %s, from uuid: %s" % (originalDir+filename[1], filename[0]) 
        except:
                print "<b>Unable to find file (exception thrown) %s, from uuid: %s" % (originalDir+filename[1], filename[0])    


    exportAttributes = {}
    for aenttypename, attributename, newFilename, uuid in exportPhotos:
        if aenttypename not in realExportList:
            realExportList[aenttypename] = {}
            exportAttributes[aenttypename] = attributename
        if uuid not in realExportList[aenttypename]:
            realExportList[aenttypename][uuid] = []

        realExportList[aenttypename][uuid].append(newFilename)
    
    #print "    ",realExportList
    
    for aenttypename in realExportList:
        #print aenttypename, realExportList[aenttypename]
        for uuid in realExportList[aenttypename]:
            exportCon.execute("update %s set %s = ? where uuid = ?" % (aenttypename, exportAttributes[aenttypename]), (', '.join(realExportList[aenttypename][uuid]), uuid))
    exportCon.commit()

    # check input flag as to what filename to export




for row in importCon.execute("select aenttypename, geometrytype(geometryn(geospatialcolumn,1)) as geomtype, count(distinct geometrytype(geometryn(geospatialcolumn,1))) from latestnondeletedarchent join aenttype using (aenttypeid) where geomtype is not null group by aenttypename having  count(distinct geometrytype(geometryn(geospatialcolumn,1))) = 1"):
    cmd = ["spatialite_tool", "-e", "-shp", "%s" % (clean(row[0]).decode("ascii")), "-d", "%sshape.sqlite3" % (exportDir), "-t", "%s" % (clean(row[0])), "-c", "utf-8", "-g", "geospatialcolumn", "-s", "%s" % (srid), "--type", "%s" % (row[1])]
    files.append("%s.dbf" % (clean(row[0])))
    files.append("%s.shp" % (clean(row[0])))
    files.append("%s.shx" % (clean(row[0])))
    # print cmd
    subprocess.call(cmd, cwd=exportDir)
'''
for at in importCon.execute("select aenttypename from aenttype"):
    aenttypename = "%s" % (clean(at[0]))


    cursor = exportCon.cursor()
    try:
        cursor.execute("select * from %s" % (aenttypename)) 
    except:
        cursor.execute("select * from %s" % (aenttypename))     


    files.append("Entity-%s.csv" % (aenttypename))

    csv_writer = UnicodeWriter(open(exportDir+"Entity-%s.csv" % (aenttypename), "wb+"))
    csv_writer.writerow([i[0] for i in cursor.description]) # write headers
    csv_writer.writerows(cursor)

    #spatialite_tool -e -shp surveyUnitTransectBuffer -d db.sqlite3 -t surveyUnitWithTransectBuffer -c utf-8 -g surveyBuffer --type polygon
'''




relntypequery = '''select distinct relntypeid, relntypename from relntype join latestnondeletedrelationship using (relntypeid);'''

relnquery = '''select distinct parent.uuid as parentuuid, child.uuid as childuuid, parent.participatesverb
                 from latestnondeletedaentreln parent 
                 join latestnondeletedaentreln child using (relationshipid)
                 join relationship using (relationshipid)
                 join relntype using (relntypeid)
                where parent.uuid != child.uuid
                  and relntypename = ?'''


relntypecursor = importCon.cursor()
relncursor = importCon.cursor()
for relntypeid, relntypename in relntypecursor.execute(relntypequery): 
    relncursor.execute(relnquery, [relntypename])
    #print relntypename

    exportCon.execute("CREATE TABLE %s (parentuuid TEXT, childuuid TEXT, participatesverb TEXT);" % (clean(relntypename)))
    for i in relncursor:
        exportCon.execute("INSERT INTO %s VALUES(?,?,?)" % (clean(relntypename)), i)

    #files.append("Relationship-%s.csv" % (clean(relntypename)))
    #csv_writer = UnicodeWriter(open(exportDir+"Relationship-%s.csv" % (clean(relntypename)), "wb+"))
    #csv_writer.writerow([i[0] for i in relncursor.description]) # write headers
    #csv_writer.writerows(relncursor)


stoneQuery = '''
    select  replace(replace(stoneartefactclusters.StoneGridSquare,'Grid Square ',''),' - ','') as 'Sq',
                replace(StoneIDNumber,'Stone ','') as 'ID',
                'Stone' as 'Site',
                StoneInSituStoneArtefacts as 'Insit Stone',
                StoneInSituChippedStoneArtefacts as 'Insit CS',
                StoneInSituRetouchedArtefacts as 'Insit Ret',
                StoneInSituChippedStoneRawMaterial as 'Insit CS Raw Mat',
                StoneInSituUnmodifiedStoneTypes as 'Insit Unmod',
                StoneInSituUnmodifiedStoneRawMaterial as 'Insit Unmod Raw Mat',
                StoneInSituGroundStoneTypes as 'Insit GS',
                StoneInSituGroundStoneStatus as 'Insit GS Status',
                StoneInSituGroundStoneRawMaterial as 'Insit GS Raw Mat',
                StoneInSituSurfaceModification as 'Insit Mod',
                StoneSurfaceStoneArtefacts as 'Surf Stone',
                StoneSurfaceChippedStoneArtefacts as 'Surf CS',
                StoneSurfaceRetouchedArtefacts as 'Surf Ret',
                StoneSurfaceChippedStoneRawMaterial as 'Surf CS Raw Mat',
                StoneSurfaceUnmodifiedStoneTypes as 'Surf Unmod',
                StoneSurfaceUnmodifiedStoneRawMaterial as 'Surf Unmod Raw Mat',
                StoneSurfaceGroundStoneTypes as 'Surf GS',
                StoneSurfaceGroundStoneStatus as 'Surf GS Status',
                StoneSurfaceGroundStoneRawMaterial as 'Surf GS Raw Mat',
                StoneSurfaceSurfaceModification as 'Surd Mod',
                coalesce(StoneInSituPotentialRefits,'') || coalesce(StoneSurfacePotentialRefits,'') as 'Insit / Surf Pot Refit',
                group_concat(StoneAssociatedInsitu.StoneInSitu,' | ') as 'Insitu Assoc',
                group_concat(StoneAssociatedSurface.StoneSurface,' | ') as 'Surf Assoc',
                group_concat(StoneAssociatedInsitu.StoneHearth,' | ') as 'Insit Hearth',
                group_concat(StoneAssociatedSurface.StoneHearth,' | ') as 'Surf Hearth',
                group_concat(StoneAssociatedInsitu.StoneLacustrine,' | ') as 'Insit Lacust',
                group_concat(StoneAssociatedInsitu.StoneBurntlacustrinematerial,' | ') as 'Insit Burned Lacust',
                group_concat(StoneAssociatedSurface.StoneLacustrine,' | ') as 'Surf Lacust',
                group_concat(StoneAssociatedSurface.StoneBurntlacustrinematerial,' | ') as 'Surf Burned Lacust',
                group_concat(StoneAssociatedInsitu.StoneTerrestrial,' | ') as 'Insit Terr',
                group_concat(StoneAssociatedInsitu.StoneBurntterrestrialbone,' | ') as 'Insit Burned Terr',
                group_concat(StoneAssociatedSurface.StoneTerrestrial,' | ') as 'Surf Terr',
                group_concat(StoneAssociatedSurface.StoneBurntterrestrialbone,' | ') as 'Surf Burned Terr',
                group_concat(StoneAssociatedInsitu.StoneEggshell,' | ') as 'Insit Egg',
                group_concat(StoneAssociatedInsitu.StoneBurnteggshell,' | ') as 'Insit Burned Egg',
                group_concat(StoneAssociatedSurface.StoneEggshell,' | ') as 'Surf Egg',
                group_concat(StoneAssociatedSurface.StoneBurnteggshell,' | ') as 'Surf Burned Egg',
                group_concat(StoneAssociatedInsitu.StoneOtherWorkedorTransportedMaterial,' | ') as 'Insit Other',
                group_concat(StoneAssociatedSurface.StoneOtherWorkedorTransportedMaterial,' | ') as 'Surf Other',
                StoneTopographicSetting as 'Topo',
                StoneSedimentType as 'Sed',
                StoneStratigraphicUnit as 'Strat',
                StoneVulnerabilityToErosion as 'Vulnerable',
                StonePalaeotopographicSetting as 'Palaeotopo',
                StonePhotos as 'Photos',
                StoneNotes as 'Notes',
                datetime(replace(stoneartefactclusters.createdAtGMT,'GMT',''),'localtime') as 'createdAt',
                stoneartefactclusters.createdBy as 'createdBy'
      from stoneartefactclusters 
      left outer join StoneAndAssociatedInsituMaterials on (stoneartefactclusters.uuid = StoneAndAssociatedInsituMaterials.parentuuid)
      left outer join StoneAndAssociatedSurfaceMaterials on (stoneartefactclusters.uuid = StoneAndAssociatedSurfaceMaterials.parentuuid)
      left outer join StoneAssociatedInsitu on (StoneAssociatedInsitu.uuid = StoneAndAssociatedInsituMaterials.childuuid)
      left outer join StoneAssociatedSurface on (stoneassociatedsurface.uuid = StoneAndAssociatedSurfaceMaterials.childuuid)
    group by stoneartefactclusters.uuid
    order by cast(ID as Numeric);
'''




isolatedQuery = '''
    select  replace(IsolatedIDNumber,'Isolated ','') as 'Sq',
            replace(replace(isolated.IsolatedGridSquare,'Grid Square ',''),' - ','') as 'ID',
            'Isolated' as 'Site',
            IsolatedInSituorSurface as 'Status',
            IsolatedOccurrenceType as 'Type',
            IsolatedStoneRawMaterialType as 'Raw Mat',
            IsolatedModificationtoOrganicMaterial as 'Mod Org',
            IsolatedModificationtoStoneMaterial as 'Mod Inorg',
            IsolatedTopographicSetting as 'Topo',
            IsolatedSedimentType as 'Sed',
            IsolatedVulnerabilitytoErosion as 'Strat',
            IsolatedPalaeotopographicSetting as 'Vulnerable',
            IsolatedNotes as 'Palaeotopo',
            IsolatedPhotos as 'Photos',
            IsolatedStratigraphicUnit as 'Notes',
            datetime(replace(isolated.createdAtGMT,'GMT',''),'localtime') as 'createdAt',
            isolated.createdBy as 'createdBy'
    from isolated
      order by cast(ID as Numeric);
'''

shellQuery= '''

    select  replace(shellIDNumber,'Shell ','') as 'Sq',
            replace(replace(shell.shellGridSquare,'Grid Square ',''),' - ','') as 'ID',
            'Shell' as 'Site',
            ShellShellType as 'Feature',
            ShellContinuity as 'Continuity',
            ShellPresenceofcharcoal as 'Charcoal',
            ShellProportionofmaterialthatremainsinsitu as '% insit',
            ShellBivalvepreservation as 'Preservation',
            ShellBivalvedispersal as 'Dispersal',
            group_concat(ShellAssocAssociatedmaterial,' | ') as 'Assoc',
            group_concat(ShellAssocAssociatedHearthMaterial,' | ') as 'Hearth',
            group_concat(ShellAssocAssociatedlacustrinematerial,' | ') as 'Lacust',
            group_concat(ShellAssocBurntlacustrinematerial,' | ') as 'Burned Lacust',
            group_concat(ShellAssocAssociatedterrestrialbone,' | ') as 'Terr',
            group_concat(ShellAssocBurntterrestrialbone,' | ') as 'Burned Terr',
            group_concat(ShellAssocAssociatedeggshell,' | ') as 'Egg',
            group_concat(ShellAssocBurnteggshell,' | ') as 'Burned Egg',
            group_concat(ShellAssocAssociatedstoneartefacts,' | ') as 'Stone',
            group_concat(ShellAssocAssociatedchippedstoneartefacts,' | ') as 'CS',
            group_concat(ShellAssocAssociatedretouchedartefacts,' | ') as 'Ret',
            group_concat(ShellAssocChippedStoneRawMaterial,' | ') as 'CS Raw Mat',
            group_concat(ShellAssocAssociatedunmodifiedstone,' | ') as 'Unmod',
            group_concat(ShellAssocUnmodifiedRawMaterial,' | ') as 'Unmod Raw Mat',
            group_concat(ShellAssocGroundstonetypespresent,' | ') as 'GS',
            group_concat(ShellAssocGroundstonestatus,' | ') as 'GS Status',
            group_concat(ShellAssocGroundstonerawmaterial,' | ') as 'GS Raw Mat',
            group_concat(ShellAssocAssociatedotherworkedortransportedmaterial,' | ') as 'Other',
            ShellTopographicSetting as 'Topo',
            ShellSedimentType as 'Sed',
            ShellStratigraphicUnit as 'Strat',
            ShellVulnerabilityToErosion as 'Vulnerable',
            ShellPalaeotopographicSetting as 'Palaeotopo',
            ShellPhotos as 'Photos',
            ShellNotes as 'Notes',
            datetime(replace(shell.createdAtGMT,'GMT',''),'localtime') as 'createdAt',
            shell.createdBy as 'createdBy'
    from shell 
    left outer join ShellAndAssociatedMaterials on (shell.uuid = ShellAndAssociatedMaterials.parentuuid)
    left outer join ShellAssociatedMaterials on (ShellAssociatedMaterials.uuid = ShellAndAssociatedMaterials.childuuid)
    group by shell.uuid
    order by cast(ID as Numeric);
'''

hearthQuery = '''

    select  replace(hearthIDNumber,'Hearth ','') as 'Sq',
            replace(replace(hearth.hearthGridSquare,'Grid Square ',''),' - ','') as 'ID',
            'Hearth' as 'Site',
            HearthHearthType as 'Feature',
            HearthBriefdescription as 'Desc',
            HearthCharcoal as 'Charcoal',
            HearthProportionofmaterialthatremainsinsitu as '% insit',
            HearthModificationofheatretainerhearths as 'Mod HRH',
            HearthModificationofnonheatretainerhearths as 'Mod non HRH',
            group_concat(HearthAssocAssociatedmaterial,' | ') as 'Assoc',
            group_concat(HearthAssocAssociatedlacustrinematerial,' | ') as 'Lacust',
            group_concat(HearthAssocBurntlacustrinematerial,' | ') as 'Burned Lacust',
            group_concat(HearthAssocAssociatedterrestrialbone,' | ') as 'Terr',
            group_concat(HearthAssocBurntterrestrialbone,' | ') as 'Burned Terr',
            group_concat(HearthAssocAssociatedeggshell,' | ') as 'Egg',
            group_concat(HearthAssocBurnteggshell,' | ') as 'Burned Egg',
            group_concat(HearthAssocAssociatedstoneartefacts,' | ') as 'Stone',
            group_concat(HearthAssocAssociatedchippedstoneartefacts,' | ') as 'CS',
            group_concat(HearthAssocAssociatedretouchedartefacts,' | ') as 'Ret',
            group_concat(HearthAssocChippedStoneRawMaterial,' | ') as 'CS Raw Mat',
            group_concat(HearthAssocAssociatedunmodifiedstone,' | ') as 'Unmod',
            group_concat(HearthAssocUnmodifiedRawMaterial,' | ') as 'Unmod Raw Mat',
            group_concat(HearthAssocGroundstonetypespresent,' | ') as 'GS',
            group_concat(HearthAssocGroundstonestatus,' | ') as 'GS Status',
            group_concat(HearthAssocGroundstonerawmaterial,' | ') as 'GS Raw Mat',
            group_concat(HearthAssocAssociatedotherworkedortransportedmaterial,' | ') as 'Other',
            HearthTopographicSetting as 'Topo',
            HearthSedimentType as 'Sed',
            HearthStratigraphicUnit as 'Strat',
            HearthVulnerabilityToErosion as 'Vulnerable',
            HearthPalaeotopographicSetting as 'Palaeotopo',
            HearthPhotos as 'Photos',
            HearthNotes as 'Notes',
            datetime(replace(hearth.createdAtGMT,'GMT',''),'localtime') as 'createdAt',
            hearth.createdBy as 'createdBy'    
      from hearth 
      left outer join HearthAndAssociatedMaterials on (hearth.uuid = HearthAndAssociatedMaterials.parentuuid)
      left outer join HearthAssociatedMaterials on (HearthAssociatedMaterials.uuid = HearthAndAssociatedMaterials.childuuid)
    group by hearth.uuid
    order by cast(ID as Numeric);
'''
boneQuery = '''
select  replace(oldboneIDNumber,'Bone ','') as 'ID',
            replace(replace(bone.oldboneGridSquare,'Grid Square ',''),' - ','') as 'Sq',
            'Bone' as 'Site',
            OldBoneClusterType as 'Feature',
            OldBoneProportionofmaterialthatremainsinsitu as '% insit',
            OldBoneBodyPartsIdentifed as 'Body Parts',
            OldBoneTaxonIdentified as 'Taxa',
            OldBoneBonePreservation as 'Preservation',
            OldBoneDeliberateSurfaceModification as 'Surf Mod',
            group_concat(OldBoneAssociatedinsitumaterial,' | ') as 'Insitu Assoc',
            group_concat(BoneAssociatedSurfaceMaterials.OldBoneAssociatedsurfacematerial,' | ') as 'Surf Assoc',
            group_concat(BoneAssociatedInsituMaterials.OldBoneBivalvepreservation,' | ') as 'Insit Bivalve Pres',
            group_concat(BoneAssociatedInsituMaterials.OldBoneBurnedMussel,' | ') as 'Insit Burned Bivalve',
            group_concat(BoneAssociatedSurfaceMaterials.OldBoneBivalvepreservation,' | ') as 'Surf Bivalve Pres',
            group_concat(BoneAssociatedSurfaceMaterials.OldBoneBurnedMussel,' | ') as 'Surf Burned Bivalve',
            group_concat(BoneAssociatedInsituMaterials.OldBoneAssociatedInSituHearthMaterial,' | ') as 'Insit Hearth',
            group_concat(BoneAssociatedSurfaceMaterials.OldBoneAssociatedSurfaceHearthMaterial,' | ') as 'Surf Hearth',
            group_concat(BoneAssociatedInsituMaterials.OldBoneAssociatedEggshell,' | ') as 'Insit Egg',
            group_concat(BoneAssociatedInsituMaterials.OldBoneBurnedEggshel,' | ') as 'Insit Burned Egg',
            group_concat(BoneAssociatedSurfaceMaterials.OldBoneAssociatedEggshell,' | ') as 'Surf Egg',
            group_concat(BoneAssociatedSurfaceMaterials.OldBoneBurnedEggshel,' | ') as 'Surf Burned Egg',
            group_concat(BoneAssociatedInsituMaterials.OldBoneAssociatedStoneArtefacts,' | ') as 'Insit Stone',
            group_concat(BoneAssociatedSurfaceMaterials.OldBoneAssociatedStoneArtefacts,' | ') as 'Surf Stone',
            group_concat(BoneAssociatedInsituMaterials.OldBoneAssociatedChippedStoneArtefacts,' | ') as 'Insit CS',
            group_concat(BoneAssociatedInsituMaterials.OldBoneAssociatedRetouchedArtefacts,' | ') as 'Insit Ret',
            group_concat(BoneAssociatedInsituMaterials.OldBoneChippedStoneRawMaterial,' | ') as 'Insit CS Raw Mat',
            group_concat(BoneAssociatedSurfaceMaterials.OldBoneAssociatedChippedStoneArtefacts,' | ') as 'Surf CS',
            group_concat(BoneAssociatedSurfaceMaterials.OldBoneAssociatedRetouchedArtefacts,' | ') as 'Surf Ret',
            group_concat(BoneAssociatedSurfaceMaterials.OldBoneChippedStoneRawMaterial,' | ') as 'Surf CS Raw Mat',
            group_concat(BoneAssociatedInsituMaterials.OldBoneAssociatedUnmodifiedStone,' | ') as 'Insit Unmod',
            group_concat(BoneAssociatedInsituMaterials.OldBoneUnmodifiedStoneRawMaterial,' | ') as 'Insit Unmod Raw Mat',
            group_concat(BoneAssociatedSurfaceMaterials.OldBoneAssociatedUnmodifiedStone,' | ') as 'Surf Unmod',
            group_concat(BoneAssociatedSurfaceMaterials.OldBoneUnmodifiedStoneRawMaterial,' | ') as 'Surf Unmod Raw Mat',
            group_concat(BoneAssociatedInsituMaterials.OldBoneGroundStoneTypesPresent,' | ') as 'Insit GS',
            group_concat(BoneAssociatedInsituMaterials.OldBoneGroundStoneStatus,' | ') as 'Insit GS Status',
            group_concat(BoneAssociatedInsituMaterials.OldBoneGroundStoneRawMaterial,' | ') as 'Insit GS Raw Mat',
            group_concat(BoneAssociatedSurfaceMaterials.OldBoneGroundStoneTypesPresent,' | ') as 'Surf GS',
            group_concat(BoneAssociatedSurfaceMaterials.OldBoneGroundStoneStatus,' | ') as 'Surf GS Status',
            group_concat(BoneAssociatedSurfaceMaterials.OldBoneGroundStoneRawMaterial,' | ') as 'Surf GS Raw Mat',
            group_concat(BoneAssociatedInsituMaterials.OldBoneAssociatedOtherArtefacts,' | ') as 'Insit Other',
            group_concat(BoneAssociatedSurfaceMaterials.OldBoneAssociatedOtherArtefacts,' | ') as 'Surf Other',
            OldBoneTopographicSetting as 'Topo',
            OldBoneSedimentType as 'Sed',
            OldBoneStratigraphicUnit as 'Strat',
            OldBoneVulnerabilityToErosion as 'Vulnerable',
            OldBonePalaeotopographicSetting as 'Palaeotopo',
            OldBonePhotos as 'Photos',
            OldBoneNotes as 'Notes',
            datetime(replace(bone.createdAtGMT,'GMT',''),'localtime') as 'createdAt',
            bone.createdBy as 'createdBy'
    from bone
      left outer join BoneAndAssociatedInsituMaterials on (bone.uuid = BoneAndAssociatedInsituMaterials.parentuuid)
      left outer join BoneAndAssociatedSurfaceMaterials on (bone.uuid = BoneAndAssociatedSurfaceMaterials.parentuuid)
      left outer join BoneAssociatedInsituMaterials on (BoneAssociatedInsituMaterials.uuid = BoneAndAssociatedInsituMaterials.childuuid)
      left outer join BoneAssociatedSurfaceMaterials on (BoneAssociatedSurfaceMaterials.uuid = BoneAndAssociatedSurfaceMaterials.childuuid)
    group by bone.uuid
    order by cast(ID as Numeric);
'''


def outputTable(tablename, query):       
    try: 
        tableCursor = exportCon.cursor()
        
        
        if tableCursor.execute(query):
            files.append("%s.csv" % (tablename))
            csv_writer = UnicodeWriter(open(exportDir+"%s.csv" % (tablename), "wb+"))
            csv_writer.writerow([i[0] for i in tableCursor.description]) # write headers
            csv_writer.writerows(tableCursor)
    except:
        print "Unexpected error:", sys.exc_info()[0]
        print tablename, query


outputTable('stone',stoneQuery)
outputTable('isolated',isolatedQuery)
outputTable('shell',shellQuery)
outputTable('hearth',hearthQuery)
outputTable('bone',boneQuery)

tarf = tarfile.open("%s/%s-export.tar.bz2" % (finalExportDir,moduleName), 'w:bz2')
try:
    for file in files:
        tarf.add(exportDir+file, arcname=moduleName+'/'+file)
finally:
    tarf.close()


try:
    os.remove(exportDir)
except OSError:
    pass

