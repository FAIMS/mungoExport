attach database 'original/db.sqlite3' as original;

drop table if exists stoneartefactclusterscsv;
drop table if exists isolatedcsv;
drop table if exists shellcsv;
drop table if exists hearthcsv;
drop table if exists bonecsv;
.mode csv
.import LakeMungo/Entity-StoneArtefactClusters.csv stoneartefactclusterscsv
.import LakeMungo/Entity-Isolated.csv isolatedcsv
.import LakeMungo/Entity-Shell.csv shellcsv
.import LakeMungo/Entity-Hearth.csv hearthcsv
.import LakeMungo/Entity-Bone.csv bonecsv


.out stone.csv
	select 	replace(replace(stoneartefactclusters.StoneGridSquare,'Grid Square ',''),' - ','') as GridSquare,
			'Stone' as SiteType,
			replace(StoneIDNumber,'Stone ','') as IDNumber,
			StoneInSituStoneArtefacts as InSituStoneArtefacts,
			StoneInSituChippedStoneArtefacts as InSituChippedStoneArtefacts,
			StoneInSituRetouchedArtefacts as InSituRetouchedArtefacts,
			StoneInSituChippedStoneRawMaterial as InSituChippedStoneRawMaterial,
			StoneInSituUnmodifiedStoneTypes as InSituUnmodifiedStoneTypes,
			StoneInSituUnmodifiedStoneRawMaterial as InSituUnmodifiedStoneRawMaterial,
			StoneInSituUnmodifiedRawMaterials as InSituUnmodifiedRawMaterials,
			StoneInSituGroundStoneTypes as InSituGroundStoneTypes,
			StoneInSituGroundStoneStatus as InSituGroundStoneStatus,
			StoneInSituGroundStoneRawMaterial as InSituGroundStoneRawMaterial,
			StoneInSituSurfaceModification as InSituSurfaceModification,
			StoneSurfaceStoneArtefacts as SurfaceStoneArtefacts,
			StoneSurfaceChippedStoneArtefacts as SurfaceChippedStoneArtefacts,
			StoneSurfaceRetouchedArtefacts as SurfaceRetouchedArtefacts,
			StoneSurfaceChippedStoneRawMaterial as SurfaceChippedStoneRawMaterial,
			StoneSurfaceUnmodifiedStoneTypes as SurfaceUnmodifiedStoneTypes,
			StoneSurfaceUnmodifiedStoneRawMaterial as SurfaceUnmodifiedStoneRawMaterial,
			StoneSurfaceGroundStoneTypes as SurfaceGroundStoneTypes,
			StoneSurfaceGroundStoneStatus as SurfaceGroundStoneStatus,
			StoneSurfaceGroundStoneRawMaterial as SurfaceGroundStoneRawMaterial,
			StoneSurfaceSurfaceModification as SurfaceSurfaceModification,
			StoneInSituPotentialRefits as InSituPotentialRefits,
			StoneSurfacePotentialRefits as SurfacePotentialRefits,
			group_concat(StoneAssociatedInsitu.StoneInSitu,' | ') as InSitu_InSitu, 
			group_concat(StoneAssociatedSurface.StoneSurface,' | ') as Surface_Surface,
			group_concat(StoneAssociatedInsitu.StoneHearth,' | ') as InSitu_Hearth, 
			group_concat(StoneAssociatedSurface.StoneHearth,' | ') as Surface_Hearth,
			group_concat(StoneAssociatedInsitu.StoneLacustrine,' | ') as InSitu_Lacustrine, 
			group_concat(StoneAssociatedInsitu.StoneBurntlacustrinematerial,' | ') as InSitu_Burntlacustrinematerial, 
			group_concat(StoneAssociatedSurface.StoneLacustrine,' | ') as Surface_Lacustrine,
			group_concat(StoneAssociatedSurface.StoneBurntlacustrinematerial,' | ') as Surface_Burntlacustrinematerial,
			group_concat(StoneAssociatedInsitu.StoneTerrestrial,' | ') as InSitu_Terrestrial, 
			group_concat(StoneAssociatedInsitu.StoneBurntterrestrialbone,' | ') as InSitu_Burntterrestrialbone, 
			group_concat(StoneAssociatedSurface.StoneTerrestrial,' | ') as Surface_Terrestrial,
			group_concat(StoneAssociatedSurface.StoneBurntterrestrialbone,' | ') as Surface_Burntterrestrialbone,
			group_concat(StoneAssociatedInsitu.StoneEggshell,' | ') as InSitu_Eggshell, 
			group_concat(StoneAssociatedInsitu.StoneBurnteggshell,' | ') as InSitu_Burnteggshell,
			group_concat(StoneAssociatedSurface.StoneEggshell,' | ') as Surface_Eggshell,
			group_concat(StoneAssociatedSurface.StoneBurnteggshell,' | ') as Surface_Burnteggshell,
			group_concat(StoneAssociatedInsitu.StoneOtherWorkedorTransportedMaterial,' | ') as InSitu_OtherWorkedorTransportedMaterial, 
			group_concat(StoneAssociatedSurface.StoneOtherWorkedorTransportedMaterial,' | ') as Surface_OtherWorkedorTransportedMaterial,
			StoneTopographicSetting as TopographicSetting,
			StoneSedimentType as SedimentType,
			StoneStratigraphicUnit as StratigraphicUnit,
			StoneVulnerabilityToErosion as VulnerabilityToErosion,
			StonePalaeotopographicSetting as PalaeotopographicSetting,
			stoneartefactclusterscsv.StonePhotos as Photos,
			StoneNotes as Notes,
			group_concat(StoneAssociatedSurface.StoneInSitu,' | ') as Surface_InSitu,
			group_concat(StoneAssociatedInsitu.StoneSurface,' | ') as InSitu_Surface,
			datetime(replace(stoneartefactclusters.createdAtGMT,'GMT',''),'localtime') as createdAt,
			stoneartefactclusters.createdBy as createdBy
  from stoneartefactclusters 
  join (select uuid, stonephotos from stoneartefactclusterscsv) as stoneartefactclusterscsv using (uuid)
  left outer join       
       (select distinct parent.uuid as parentuuid, child.uuid as childuuid
          from original.latestnondeletedaentreln parent 
          join original.latestnondeletedaentreln child using (relationshipid)
         where parent.uuid != child.uuid) as parentchild on (stoneartefactclusters.uuid = parentchild.parentuuid)
  left outer join StoneAssociatedInsitu on (StoneAssociatedInsitu.uuid = parentchild.childuuid)
  left outer join StoneAssociatedSurface on (stoneassociatedsurface.uuid = parentchild.childuuid)
group by stoneartefactclusters.uuid
order by createdAt, cast(IDNumber as Numeric);

.out isolated.csv
select 	replace(replace(isolated.IsolatedGridSquare,'Grid Square ',''),' - ','') as GridSquare,
		'Isolated' as SiteType,
		replace(IsolatedIDNumber,'Isolated ','') as IDNumber,
		IsolatedInSituorSurface as InSituorSurface,
		IsolatedOccurrenceType as OccurrenceType,
		IsolatedStoneRawMaterialType as StoneRawMaterialType,
		IsolatedModificationtoOrganicMaterial as ModificationtoOrganicMaterial,
		IsolatedModificationtoStoneMaterial as ModificationtoStoneMaterial,
		IsolatedTopographicSetting as TopographicSetting,
		IsolatedSedimentType as SedimentType,
		IsolatedVulnerabilitytoErosion as VulnerabilitytoErosion,
		IsolatedPalaeotopographicSetting as PalaeotopographicSetting,
		IsolatedNotes as Notes,
		isolatedcsv.IsolatedPhotos as Photos,
		IsolatedStratigraphicUnit as StratigraphicUnit,
		datetime(replace(isolated.createdAtGMT,'GMT',''),'localtime') as createdAt,
		isolated.createdBy as createdBy
from isolated
  join (select uuid, isolatedphotos from isolatedcsv) as isolatedcsv using (uuid)
  order by createdAt, cast(IDNumber as Numeric);

.out shell.csv

select	replace(replace(shell.shellGridSquare,'Grid Square ',''),' - ','') as GridSquare,
		'Shell' as SiteType,
		replace(shellIDNumber,'Shell ','') as IDNumber,
		ShellShellType as ShellType,
		ShellContinuity as Continuity,
		ShellPresenceofcharcoal as Presenceofcharcoal,
		ShellProportionofmaterialthatremainsinsitu as Proportionofmaterialthatremainsinsitu,
		ShellBivalvepreservation as Bivalvepreservation,
		ShellBivalvedispersal as Bivalvedispersal,
		group_concat(ShellAssocAssociatedmaterial,' | ') as AssociatedMaterial_Associatedmaterial,
		group_concat(ShellAssocAssociatedHearthMaterial,' | ') as AssociatedMaterial_AssociatedHearthMaterial,
		group_concat(ShellAssocAssociatedlacustrinematerial,' | ') as AssociatedMaterial_Associatedlacustrinematerial,
		group_concat(ShellAssocBurntlacustrinematerial,' | ') as AssociatedMaterial_Burntlacustrinematerial,
		group_concat(ShellAssocAssociatedterrestrialbone,' | ') as AssociatedMaterial_Associatedterrestrialbone,
		group_concat(ShellAssocBurntterrestrialbone,' | ') as AssociatedMaterial_Burntterrestrialbone,
		group_concat(ShellAssocAssociatedeggshell,' | ') as AssociatedMaterial_Associatedeggshell,
		group_concat(ShellAssocBurnteggshell,' | ') as AssociatedMaterial_Burnteggshell,
		group_concat(ShellAssocAssociatedstoneartefacts,' | ') as AssociatedMaterial_Associatedstoneartefacts,
		group_concat(ShellAssocAssociatedchippedstoneartefacts,' | ') as AssociatedMaterial_Associatedchippedstoneartefacts,
		group_concat(ShellAssocAssociatedretouchedartefacts,' | ') as AssociatedMaterial_Associatedretouchedartefacts,
		group_concat(ShellAssocChippedStoneRawMaterial,' | ') as AssociatedMaterial_ChippedStoneRawMaterial,
		group_concat(ShellAssocAssociatedunmodifiedstone,' | ') as AssociatedMaterial_Associatedunmodifiedstone,
		group_concat(ShellAssocUnmodifiedStoneTypes,' | ') as UnmodifiedStoneTypes,
		group_concat(ShellAssocUnmodifiedRawMaterial,' | ') as AssociatedMaterial_UnmodifiedRawMaterial,
		group_concat(ShellAssocGroundstonetypespresent,' | ') as AssociatedMaterial_Groundstonetypespresent,
		group_concat(ShellAssocGroundstonestatus,' | ') as AssociatedMaterial_Groundstonestatus,
		group_concat(ShellAssocGroundstonerawmaterial,' | ') as AssociatedMaterial_Groundstonerawmaterial,
		group_concat(ShellAssocAssociatedotherworkedortransportedmaterial,' | ') as AssociatedMaterial_Associatedotherworkedortransportedmaterial,
		ShellTopographicSetting as TopographicSetting,
		ShellSedimentType as SedimentType,
		ShellStratigraphicUnit as StratigraphicUnit,
		ShellVulnerabilityToErosion as VulnerabilityToErosion,
		ShellPalaeotopographicSetting as PalaeotopographicSetting,
		shellcsv.ShellPhotos as Photos,
		ShellNotes as Notes,
		datetime(replace(shell.createdAtGMT,'GMT',''),'localtime') as createdAt,
		shell.createdBy as createdBy
from shell 
join (select uuid, shellphotos from shellcsv) as shellcsv using (uuid)
left outer join       
       (select distinct parent.uuid as parentuuid, child.uuid as childuuid
          from original.latestnondeletedaentreln parent 
          join original.latestnondeletedaentreln child using (relationshipid)
         where parent.uuid != child.uuid) as parentchild on (shell.uuid = parentchild.parentuuid)
  left outer join ShellAssociatedMaterials on (ShellAssociatedMaterials.uuid = parentchild.childuuid)
group by shell.uuid
order by createdAt, cast(IDNumber as Numeric);

.out hearth.csv

select 	replace(replace(hearth.hearthGridSquare,'Grid Square ',''),' - ','') as GridSquare,
		'Hearth' as SiteType,
		replace(hearthIDNumber,'Hearth ','') as IDNumber,
		HearthHearthType as HearthType,
		HearthBriefdescription as Briefdescription,
		HearthCharcoal as Charcoal,
		HearthProportionofmaterialthatremainsinsitu as Proportionofmaterialthatremainsinsitu,
		HearthModificationofheatretainerhearths as Modificationofheatretainerhearths,
		HearthModificationofnonheatretainerhearths as Modificationofnonheatretainerhearths,
		group_concat(HearthAssocAssociatedmaterial,' | ') as Associatedmaterial,
		group_concat(HearthAssocAssociatedlacustrinematerial,' | ') as Associatedlacustrinematerial,
		group_concat(HearthAssocBurntlacustrinematerial,' | ') as Burntlacustrinematerial,
		group_concat(HearthAssocAssociatedterrestrialbone,' | ') as Associatedterrestrialbone,
		group_concat(HearthAssocBurntterrestrialbone,' | ') as Burntterrestrialbone,
		group_concat(HearthAssocAssociatedeggshell,' | ') as Associatedeggshell,
		group_concat(HearthAssocBurnteggshell,' | ') as Burnteggshell,
		group_concat(HearthAssocAssociatedstoneartefacts,' | ') as Associatedstoneartefacts,
		group_concat(HearthAssocAssociatedchippedstoneartefacts,' | ') as Associatedchippedstoneartefacts,
		group_concat(HearthAssocAssociatedretouchedartefacts,' | ') as Associatedretouchedartefacts,
		group_concat(HearthAssocChippedStoneRawMaterial,' | ') as ChippedStoneRawMaterial,
		group_concat(HearthAssocAssociatedunmodifiedstone,' | ') as Associatedunmodifiedstone,
		group_concat(HearthAssocUnmodifiedRawMaterial,' | ') as UnmodifiedRawMaterial,
		group_concat(HearthAssocGroundstonetypespresent,' | ') as Groundstonetypespresent,
		group_concat(HearthAssocGroundstonestatus,' | ') as Groundstonestatus,
		group_concat(HearthAssocGroundstonerawmaterial,' | ') as Groundstonerawmaterial,
		group_concat(HearthAssocAssociatedotherworkedortransportedmaterial,' | ') as Associatedotherworkedortransportedmaterial,
		HearthTopographicSetting as TopographicSetting,
		HearthSedimentType as SedimentType,
		HearthStratigraphicUnit as StratigraphicUnit,
		HearthVulnerabilityToErosion as VulnerabilityToErosion,
		HearthPalaeotopographicSetting as PalaeotopographicSetting,
		hearthcsv.HearthPhotos as Photos,
		HearthNotes as Notes,
		datetime(replace(hearth.createdAtGMT,'GMT',''),'localtime') as createdAt,
		hearth.createdBy as createdBy		
  from hearth 
  join (select uuid, hearthphotos from hearthcsv) as hearthcsv using (uuid)
  left outer join       
       (select distinct parent.uuid as parentuuid, child.uuid as childuuid
          from original.latestnondeletedaentreln parent 
          join original.latestnondeletedaentreln child using (relationshipid)
         where parent.uuid != child.uuid) as parentchild on (hearthcsv.uuid = parentchild.parentuuid)
  left outer join HearthAssociatedMaterials on (HearthAssociatedMaterials.uuid = parentchild.childuuid)
group by hearth.uuid
order by createdAt, cast(IDNumber as Numeric);
.out bone.csv

select	replace(replace(bone.oldboneGridSquare,'Grid Square ',''),' - ','') as GridSquare,
		'Bone' as SiteType,
		replace(oldboneIDNumber,'Bone ','') as IDNumber,
		OldBoneClusterType as ClusterType,
		OldBoneProportionofmaterialthatremainsinsitu as Proportionofmaterialthatremainsinsitu,
		OldBoneBodyPartsIdentifed as BodyPartsIdentifed,
		OldBoneTaxonIdentified as TaxonIdentified,
		OldBoneBonePreservation as BonePreservation,
		OldBoneDeliberateSurfaceModification as DeliberateSurfaceModification,
		group_concat(OldBoneAssociatedinsitumaterial,' | ') as InSitu_Associatedinsitumaterial,
		group_concat(BoneAssociatedSurfaceMaterials.OldBoneAssociatedsurfacematerial,' | ') as Surface_Associatedsurfacematerial,
		group_concat(BoneAssociatedInsituMaterials.OldBoneBivalvepreservation,' | ') as InSitu_Bivalvepreservation,
		group_concat(BoneAssociatedInsituMaterials.OldBoneBurnedMussel,' | ') as InSitu_BurnedMussel,
		group_concat(BoneAssociatedSurfaceMaterials.OldBoneBivalvepreservation,' | ') as Surface_Bivalvepreservation,
		group_concat(BoneAssociatedSurfaceMaterials.OldBoneBurnedMussel,' | ') as Surface_BurnedMussel,
		group_concat(BoneAssociatedInsituMaterials.OldBoneAssociatedInSituHearthMaterial,' | ') as InSitu_AssociatedInSituHearthMaterial,
		group_concat(BoneAssociatedSurfaceMaterials.OldBoneAssociatedSurfaceHearthMaterial,' | ') as Surface_AssociatedSurfaceHearthMaterial,
		group_concat(BoneAssociatedInsituMaterials.OldBoneAssociatedEggshell,' | ') as InSitu_AssociatedEggshell,
		group_concat(BoneAssociatedInsituMaterials.OldBoneBurnedEggshel,' | ') as InSitu_BurnedEggshel,
		group_concat(BoneAssociatedSurfaceMaterials.OldBoneAssociatedEggshell,' | ') as Surface_AssociatedEggshell,
		group_concat(BoneAssociatedSurfaceMaterials.OldBoneBurnedEggshel,' | ') as Surface_BurnedEggshel,
		group_concat(BoneAssociatedInsituMaterials.OldBoneAssociatedStoneArtefacts,' | ') as InSitu_AssociatedStoneArtefacts,
		group_concat(BoneAssociatedSurfaceMaterials.OldBoneAssociatedStoneArtefacts,' | ') as Surface_AssociatedStoneArtefacts,
		group_concat(BoneAssociatedInsituMaterials.OldBoneAssociatedChippedStoneArtefacts,' | ') as InSitu_AssociatedChippedStoneArtefacts,
		group_concat(BoneAssociatedInsituMaterials.OldBoneAssociatedRetouchedArtefacts,' | ') as InSitu_AssociatedRetouchedArtefacts,
		group_concat(BoneAssociatedInsituMaterials.OldBoneChippedStoneRawMaterial,' | ') as InSitu_ChippedStoneRawMaterial,
		group_concat(BoneAssociatedSurfaceMaterials.OldBoneAssociatedChippedStoneArtefacts,' | ') as Surface_AssociatedChippedStoneArtefacts,
		group_concat(BoneAssociatedSurfaceMaterials.OldBoneAssociatedRetouchedArtefacts,' | ') as Surface_AssociatedRetouchedArtefacts,
		group_concat(BoneAssociatedSurfaceMaterials.OldBoneChippedStoneRawMaterial,' | ') as Surface_ChippedStoneRawMaterial,
		group_concat(BoneAssociatedInsituMaterials.OldBoneAssociatedUnmodifiedStone,' | ') as InSitu_AssociatedUnmodifiedStone,
		group_concat(BoneAssociatedInsituMaterials.OldBoneUnmodifiedStoneRawMaterial,' | ') as InSitu_UnmodifiedStoneRawMaterial,
		group_concat(BoneAssociatedSurfaceMaterials.OldBoneAssociatedUnmodifiedStone,' | ') as Surface_AssociatedUnmodifiedStone,
		group_concat(BoneAssociatedSurfaceMaterials.OldBoneUnmodifiedStoneRawMaterial,' | ') as Surface_UnmodifiedStoneRawMaterial,
		group_concat(BoneAssociatedInsituMaterials.OldBoneGroundStoneTypesPresent,' | ') as InSitu_GroundStoneTypesPresent,
		group_concat(BoneAssociatedInsituMaterials.OldBoneGroundStoneStatus,' | ') as InSitu_GroundStoneStatus,
		group_concat(BoneAssociatedInsituMaterials.OldBoneGroundStoneRawMaterial,' | ') as InSitu_GroundStoneRawMaterial,
		group_concat(BoneAssociatedSurfaceMaterials.OldBoneGroundStoneTypesPresent,' | ') as Surface_GroundStoneTypesPresent,
		group_concat(BoneAssociatedSurfaceMaterials.OldBoneGroundStoneStatus,' | ') as Surface_GroundStoneStatus,
		group_concat(BoneAssociatedSurfaceMaterials.OldBoneGroundStoneRawMaterial,' | ') as Surface_GroundStoneRawMaterial,
		group_concat(BoneAssociatedInsituMaterials.OldBoneAssociatedOtherArtefacts,' | ') as InSitu_AssociatedOtherArtefacts,
		group_concat(BoneAssociatedSurfaceMaterials.OldBoneAssociatedOtherArtefacts,' | ') as Surface_AssociatedOtherArtefacts,
		OldBoneTopographicSetting as TopographicSetting,
		OldBoneSedimentType as SedimentType,
		OldBoneStratigraphicUnit as StratigraphicUnit,
		OldBoneVulnerabilityToErosion as VulnerabilityToErosion,
		OldBonePalaeotopographicSetting as PalaeotopographicSetting,
		bonecsv.OldBonePhotos as Photos,
		OldBoneNotes as Notes,
		datetime(replace(bone.createdAtGMT,'GMT',''),'localtime') as createdAt,
		bone.createdBy as createdBy
from bone join (select uuid, oldbonephotos from bonecsv) as bonecsv using (uuid)
left outer join       
       (select distinct parent.uuid as parentuuid, child.uuid as childuuid
          from original.latestnondeletedaentreln parent 
          join original.latestnondeletedaentreln child using (relationshipid)
         where parent.uuid != child.uuid) as parentchild on (bone.uuid = parentchild.parentuuid)
  left outer join BoneAssociatedInsituMaterials on (BoneAssociatedInsituMaterials.uuid = parentchild.childuuid)
  left outer join BoneAssociatedSurfaceMaterials on (BoneAssociatedSurfaceMaterials.uuid = parentchild.childuuid)
group by bone.uuid
order by createdAt, cast(IDNumber as Numeric);
	


	



detach database original;



