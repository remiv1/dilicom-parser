import pandas as pd
from dataclasses import dataclass

@dataclass
class FileDistri:
    header: list[str]
    footer: str
    data: pd.DataFrame

@dataclass
class DistributorDataBloc1:
    ref: str
    mvt: str
    gln: str
    rs1: str
    rs2: str | None
    numero_voie: str | None
    adresse_l1: str | None
    adresse_l2: str | None
    adresse_l3: str | None
    code_postal: str | None
    ville: str
    pays: str
    rejet_postal: str | None
    num_tel: str | None
    num_fax: str | None
    email: str | None
    website: str | None
    siren_or_siret: str | None
    num_tva_intracom: str | None
    gln_repreneur: str | None
    rs_repreneur: str | None
    fonction: str
    adherent_prisme: int

@dataclass
class DistributorDataBloc2:
    integration_commande: str
    place_commande: str
    heure_limite: str | None
    jours_collecte: str | None
    format_commandes: str | None
    type_connection: str | None
    avis_expedition: str | None

@dataclass
class DistributorDataBloc3:
    fiche_produit: int | None
    propo_commandes: int | None
    commande: int | None
    reponse_commandes: int | None
    avis_exp_v1: int | None
    avis_exp_v2: int | None
    journal_mvt: int | None
    reclamation: int | None
    retour_dde_autorisation: int | None
    retour_accord_fournisseur: int | None
    retour_avis: int | None
    facture_electronique: int | None
    demat_facture_fiscale: int | None
    centralisation_paiements: int | None

@dataclass
class DistributorLineData:
    bloc1: DistributorDataBloc1
    bloc2: DistributorDataBloc2
    bloc3: DistributorDataBloc3
    fin_ligne: str

@dataclass
class DistributorData:
    debut_fichier: str
    ref_edi: str
    date_edi: int
    lines: list[DistributorLineData]
    fin_fichier: str
