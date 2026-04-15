"""Seed the WENZE database with realistic demo data (PRD section 4.3).

20 services total: 2 per official category (1 Kinshasa RDC + 1 Brazzaville RC).
A few prices are set to 0 so the UI renders the French label "À discuter".
All user-facing text (titles, descriptions, cities, neighborhoods) is in French.

Idempotent: clears `service` and `user` tables before reinserting.

Usage (from backend/):
    python -m scripts.seed_data
"""
from __future__ import annotations

import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlmodel import Session, delete  # noqa: E402

from app.database import _ensure_anonymous_user, engine, init_db  # noqa: E402
from app.models import Category, Service, ServiceStatus, User  # noqa: E402


# --- Demo users (stable UUIDs so repeated seeds give the same ids) ---------

USERS = [
    User(
        id="11111111-1111-1111-1111-111111111001",
        name="Jean-Pierre Mabiala",
        phone_number="+243811234567",
        country="RDC",
        city_village="Kinshasa",
        neighborhood="Gombe",
    ),
    User(
        id="11111111-1111-1111-1111-111111111002",
        name="Grace Ilunga",
        phone_number="+243821234567",
        country="RDC",
        city_village="Kinshasa",
        neighborhood="Lingwala",
    ),
    User(
        id="11111111-1111-1111-1111-111111111003",
        name="Patrick Kabongo",
        phone_number="+243831234567",
        country="RDC",
        city_village="Kinshasa",
        neighborhood="Ngaliema",
    ),
    User(
        id="22222222-2222-2222-2222-222222222001",
        name="Marie Okemba",
        phone_number="+242061234567",
        country="RC",
        city_village="Brazzaville",
        neighborhood="Poto-Poto",
    ),
    User(
        id="22222222-2222-2222-2222-222222222002",
        name="Didier Nkounkou",
        phone_number="+242062234567",
        country="RC",
        city_village="Brazzaville",
        neighborhood="Moungali",
    ),
    User(
        id="22222222-2222-2222-2222-222222222003",
        name="Sylvie Mabika",
        phone_number="+242063234567",
        country="RC",
        city_village="Brazzaville",
        neighborhood="Bacongo",
    ),
]


# Boost expiry one week from now for the few boosted listings.
_BOOST_UNTIL = datetime.utcnow() + timedelta(days=7)


# --- Kinshasa services (RDC, CDF) - one per official category --------------

KINSHASA_SERVICES = [
    Service(
        user_id=USERS[0].id,
        title="Cours de maths niveau lycée",
        category=Category.SOUTIEN_SCOLAIRE,
        description="Professeur expérimenté, préparation examens d'État.",
        price=5000,
        country="RDC",
        city_village="Kinshasa",
        neighborhood="Gombe",
        whatsapp_number="+243811234567",
        phone_number="+243811234567",
        is_boosted=True,
        boost_expiry=_BOOST_UNTIL,
    ),
    Service(
        user_id=USERS[1].id,
        title="Installation électrique maison",
        category=Category.REPARATIONS_TRAVAUX,
        description="Tableau, prises, câblage complet. Devis gratuit.",
        price=25000,
        country="RDC",
        city_village="Kinshasa",
        neighborhood="Lingwala",
        whatsapp_number="+243821234567",
        phone_number="+243821234567",
    ),
    Service(
        user_id=USERS[2].id,
        title="Coiffure afro à domicile",
        category=Category.BEAUTE_COIFFURE,
        description="Tresses, dreads, soins capillaires. Je me déplace chez vous.",
        price=10000,
        country="RDC",
        city_village="Kinshasa",
        neighborhood="Ngaliema",
        whatsapp_number="+243831234567",
        phone_number="+243831234567",
    ),
    Service(
        user_id=USERS[0].id,
        title="Entretien de jardin mensuel",
        category=Category.JARDINAGE_ENTRETIEN,
        description="Tonte, taille de haies, désherbage. Forfait adaptable.",
        price=0,  # À discuter
        country="RDC",
        city_village="Kinshasa",
        neighborhood="Lemba",
        whatsapp_number="+243811234567",
        phone_number="+243811234567",
    ),
    Service(
        user_id=USERS[2].id,
        title="Plats congolais à emporter",
        category=Category.RESTAURATION_BONS_PLANS,
        description="Pondu, madesu, riz au poisson. Menu du jour.",
        price=3500,
        country="RDC",
        city_village="Kinshasa",
        neighborhood="Gombe",
        whatsapp_number="+243831234567",
        phone_number="+243831234567",
    ),
    Service(
        user_id=USERS[0].id,
        title="Livraison moto rapide",
        category=Category.TRANSPORT_LIVRAISON,
        description="Courses, colis, documents. Toute la ville.",
        price=2000,
        country="RDC",
        city_village="Kinshasa",
        neighborhood="Lingwala",
        whatsapp_number="+243811234567",
        phone_number="+243811234567",
    ),
    Service(
        user_id=USERS[1].id,
        title="Réparation smartphone écran cassé",
        category=Category.TELEPHONE_INFORMATIQUE,
        description="iPhone, Samsung, Tecno. Pièces d'origine, garantie 30 jours.",
        price=15000,
        country="RDC",
        city_village="Kinshasa",
        neighborhood="Ngaliema",
        whatsapp_number="+243821234567",
        phone_number="+243821234567",
    ),
    Service(
        user_id=USERS[2].id,
        title="Aide ménagère et lessive",
        category=Category.AIDE_MENAGERE_LESSIVE,
        description="Ménage hebdomadaire, repassage, lessive à la main.",
        price=8000,
        country="RDC",
        city_village="Kinshasa",
        neighborhood="Lemba",
        whatsapp_number="+243831234567",
        phone_number="+243831234567",
    ),
    Service(
        user_id=USERS[1].id,
        title="Menuiserie et soudure sur mesure",
        category=Category.MENUISERIE_SOUDURE,
        description="Portes, fenêtres, grilles, mobilier métallique.",
        price=20000,
        country="RDC",
        city_village="Kinshasa",
        neighborhood="Kintambo",
        whatsapp_number="+243821234567",
        phone_number="+243821234567",
    ),
    Service(
        user_id=USERS[0].id,
        title="Mécanique auto et lavage moteur",
        category=Category.MECANIQUE_AUTO_LAVAGE,
        description="Vidange, freins, diagnostic, lavage complet.",
        price=12000,
        country="RDC",
        city_village="Kinshasa",
        neighborhood="Kintambo",
        whatsapp_number="+243811234567",
        phone_number="+243811234567",
    ),
]


# --- Brazzaville services (RC, FCFA) - one per official category -----------

BRAZZAVILLE_SERVICES = [
    Service(
        user_id=USERS[3].id,
        title="Cours particuliers de physique",
        category=Category.SOUTIEN_SCOLAIRE,
        description="Terminale S, préparation Bac, exercices corrigés.",
        price=3000,
        country="RC",
        city_village="Brazzaville",
        neighborhood="Poto-Poto",
        whatsapp_number="+242061234567",
        phone_number="+242061234567",
    ),
    Service(
        user_id=USERS[4].id,
        title="Dépannage électrique d'urgence",
        category=Category.REPARATIONS_TRAVAUX,
        description="Intervention rapide 7j/7 pour courts-circuits et pannes.",
        price=7000,
        country="RC",
        city_village="Brazzaville",
        neighborhood="Moungali",
        whatsapp_number="+242062234567",
        phone_number="+242062234567",
        is_boosted=True,
        boost_expiry=_BOOST_UNTIL,
    ),
    Service(
        user_id=USERS[5].id,
        title="Tresses africaines et soins",
        category=Category.BEAUTE_COIFFURE,
        description="Tissages, défrisage, soins naturels. Salon ou à domicile.",
        price=5000,
        country="RC",
        city_village="Brazzaville",
        neighborhood="Talangaï",
        whatsapp_number="+242063234567",
        phone_number="+242063234567",
    ),
    Service(
        user_id=USERS[3].id,
        title="Tonte de pelouse et entretien",
        category=Category.JARDINAGE_ENTRETIEN,
        description="Jardinier expérimenté, matériel fourni.",
        price=0,  # À discuter
        country="RC",
        city_village="Brazzaville",
        neighborhood="Bacongo",
        whatsapp_number="+242061234567",
        phone_number="+242061234567",
    ),
    Service(
        user_id=USERS[5].id,
        title="Plats du jour maison",
        category=Category.RESTAURATION_BONS_PLANS,
        description="Saka-saka, poulet moambe, fumbwa. Commande la veille.",
        price=2500,
        country="RC",
        city_village="Brazzaville",
        neighborhood="Poto-Poto",
        whatsapp_number="+242063234567",
        phone_number="+242063234567",
    ),
    Service(
        user_id=USERS[3].id,
        title="Taxi rapide en ville",
        category=Category.TRANSPORT_LIVRAISON,
        description="Courses quotidiennes, aéroport, disponibilité 6h-22h.",
        price=1500,
        country="RC",
        city_village="Brazzaville",
        neighborhood="Moungali",
        whatsapp_number="+242061234567",
        phone_number="+242061234567",
    ),
    Service(
        user_id=USERS[4].id,
        title="Installation Wi-Fi domestique",
        category=Category.TELEPHONE_INFORMATIQUE,
        description="Box, répéteurs, couverture complète. Diagnostic gratuit.",
        price=0,  # À discuter
        country="RC",
        city_village="Brazzaville",
        neighborhood="Talangaï",
        whatsapp_number="+242062234567",
        phone_number="+242062234567",
    ),
    Service(
        user_id=USERS[5].id,
        title="Lessive et repassage à domicile",
        category=Category.AIDE_MENAGERE_LESSIVE,
        description="Lessive soignée, repassage, livraison sous 48h.",
        price=4000,
        country="RC",
        city_village="Brazzaville",
        neighborhood="Bacongo",
        whatsapp_number="+242063234567",
        phone_number="+242063234567",
    ),
    Service(
        user_id=USERS[4].id,
        title="Soudure portails et grilles",
        category=Category.MENUISERIE_SOUDURE,
        description="Fabrication et pose de portails, grilles de sécurité.",
        price=12000,
        country="RC",
        city_village="Brazzaville",
        neighborhood="Makélékélé",
        whatsapp_number="+242062234567",
        phone_number="+242062234567",
        status=ServiceStatus.ACTIVE,
    ),
    Service(
        user_id=USERS[3].id,
        title="Lavage auto à la main",
        category=Category.MECANIQUE_AUTO_LAVAGE,
        description="Lavage extérieur et intérieur, polish, à votre adresse.",
        price=3000,
        country="RC",
        city_village="Brazzaville",
        neighborhood="Makélékélé",
        whatsapp_number="+242061234567",
        phone_number="+242061234567",
    ),
]


def seed() -> None:
    init_db()
    with Session(engine) as session:
        # Wipe existing data so the seed is idempotent.
        session.exec(delete(Service))
        session.exec(delete(User))
        session.commit()

        for user in USERS:
            session.add(user)
        for service in KINSHASA_SERVICES + BRAZZAVILLE_SERVICES:
            session.add(service)
        session.commit()

    # Keep the placeholder user around so mobile POSTs still work after reseed.
    _ensure_anonymous_user()

    total = len(KINSHASA_SERVICES) + len(BRAZZAVILLE_SERVICES)
    print(f"Seeded {len(USERS)} users and {total} services "
          f"({len(KINSHASA_SERVICES)} Kinshasa / {len(BRAZZAVILLE_SERVICES)} Brazzaville).")


if __name__ == "__main__":
    seed()
