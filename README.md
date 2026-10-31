# UP Slatebook

Dépouillement de scénario et plan de travail collaboratifs pour l'équipe UP. Copie de DDC Breakdown aux couleurs UP, avec ses propres données.

**App :** https://hramilijaonina-spec.github.io/UP-Slatebook/

- Import PDF, Final Draft (.fdx), .sbx, Fountain ou texte ; découpage en scènes (INT/EXT, jour/nuit, huitièmes de page) ; retrait automatique des en-têtes et pieds de page répétés.
- Éditeur de scénario : mise en page standard (en-tête, action, personnage, didascalie, dialogue, transition, plan), Entrée/Tab, raccourcis, autocomplétion des personnages et décors, verrou par scène pendant l'écriture, export Final Draft et Fountain, impression PDF.
- Dépouillement par IA (Claude, via clé API Anthropic) dans 13 catégories, correction à la main, commentaires par scène.
- Sur téléphone, dans le Dépouillement : la scène en cours tient sur une case ; la flèche ▾ déroule la liste verticale de toutes les scènes (recherche, défilement), un appui ouvre la scène.
- Découpage technique en tableau (#Séq, #Plan, Description, Audio, Caméra, Vignette, Notes) : on écrit directement dans Description, Audio et Notes ; un clic sur Caméra ouvre le type de plan, le mouvement, l'angle et l'effet ; un clic sur #Plan ouvre la durée et les actions (monter, dupliquer, déplacer, supprimer) ; « Découper avec l'IA » propose les plans, tout reste modifiable ; vignettes photo (prise sur place ou importée) ; plans optionnels (durée 0) grisés, avec un interrupteur pour les masquer ; export PDF ou PowerPoint en paysage (une page par tranche du tableau, sans les plans optionnels) et CSV.
- **UpCopilot** (bouton flottant, administrateur et éditeurs) : on lui demande en français de redécouper une scène, de faire tenir l'épisode dans une durée, d'ajouter ou supprimer des plans, ou on lui pose une question ; il montre les changements proposés, on les applique ou les ignore, et on peut annuler après coup.
- Annuler / rétablir dans le Découpage (boutons ↶ ↷, ⌘Z / ⇧⌘Z) : modifications de cellules, plans ajoutés, supprimés ou déplacés, découpages par l'IA, actions d'UpCopilot et mises à jour du scénario.
- Mise à jour du scénario d'après le découpage : « fidèle au découpage » (immédiat, sans IA) ou « réécrit par l'IA ».
- Scénario à plusieurs épisodes : chaque épisode devient un projet, regroupés en série (ligne « Projet en cours » avec les épisodes).
- Plan de travail : lieux de tournage, journées en glisser-déposer, plan proposé automatiquement, alertes (journée chargée, déplacements, rôles éclatés).
- Suivi du tournage : case à cocher sur chaque plan du découpage (plan fait) et sur chaque scène du plan de travail (scène tournée) ; la ligne passe en vert clair, le compteur « scènes tournées » est dans le plan de travail.
- Plan de travail en journées repliables (J1, J2…) : date, scènes tournées (ex. 3/5), pages, lieux, alertes ; une journée dépliée montre ses scènes, « + Ajouter des scènes » et × pour en retirer ; case de la journée liée aux cases des scènes (tout coché = journée cochée, et inversement) ; « Tout déplier / Tout replier ». Les compteurs, pages par jour, Rapports, Lieux de tournage et Proposer un plan sont dans le menu ☰ du plan de travail ; « + Journée » est sous la dernière journée. « Proposer un plan » propose trois choix : garder ce qui est tourné (scènes tournées et leurs journées intactes, le reste replanifié à la suite), seulement les scènes à placer, ou tout refaire (avec confirmation).
- Exports (menu ☰ → Exporter) : fiches de dépouillement, plan de travail (HTML imprimable, CSV), découpage technique (CSV). Les rapports d'éléments sont dans le Plan de travail → Rapports.
- Temps réel pour toute l'équipe ; connexion avec Google ou par lien e-mail (toute adresse, sans mot de passe).
- Hors ligne : l'app s'ouvre sans réseau, les modifications sont gardées sur l'appareil et envoyées au retour de la connexion.
- Version du projet : badge v1, v2… à côté du projet (clic = historique des versions) ; menu ••• → « Nouvelle version » avec une note, pour un épisode ou toute la série ; la version apparaît dans les noms et titres des fichiers exportés.
- Scénarios « en prose » (Word, Google Docs, PDF) : en-têtes « Lieu - Moment » et répliques « Nom (indication) : texte » sont reconnus à l'import (fichier ou collage) et mis automatiquement au format scénario (INT./EXT. deviné, personnage, didascalie, dialogue, hors champ, FIN).
- Menu ☰ (à gauche, après la version) : ACCUEIL (derniers projets, Nouveau projet, Restaurer une sauvegarde ; un clic ouvre le projet) et PROJET (nouveau projet, analyse IA, export, versions, options). Export du scénario en PDF (mise en page standard, numéros de scène des deux côtés, nom de l'app en pied de page, sans adresse web).
- Sauvegarde automatique : chaque modification est enregistrée en direct ; une sauvegarde complète du projet (scénario, découpage, dépouillement, plan de travail) est créée 30 s après une série de changements (au plus toutes les 3 min). Clic sur le badge de version → liste des sauvegardes (la version actuelle est signalée) → « Revenir à cette version » : le projet reprend cet état et ce numéro de version, sans créer de nouvelle sauvegarde ; l'état d'avant reste dans la liste s'il n'y était pas déjà. L'icône corbeille d'une ligne supprime cette version (sauf la version actuelle), après confirmation. Les 40 dernières sauvegardes automatiques sont conservées, les versions nommées ne sont jamais supprimées.
- Dépouillement : clic sur un élément de la fiche → le texte de la scène défile jusqu'à son premier passage ; une barre « Rechercher » (compteur 1 / N, ↑ ↓, Entrée / Maj+Entrée, Échap) passe d'un passage à l'autre dans la scène.
- Sauvegarde : menu ••• du projet → « Sauvegarder le projet (fichier) » ; restauration dans un nouveau projet.

## Installation (une seule fois)

Le projet Firebase utilisé est `shotlist-298e2` (le même que l'app shotlist).

1. **Connexion** : console Firebase → Authentication → Méthode de connexion → activer **Google**, puis **E-mail/Mot de passe** avec l'option **Lien envoyé par e-mail (connexion sans mot de passe)**.
2. **Domaine autorisé** : Authentication → Paramètres → Domaines autorisés → ajouter `hramilijaonina-spec.github.io`.
3. **Application Web** : Paramètres du projet → Vos applications → ajouter une application Web, puis copier `apiKey` et `appId` dans `config.js`.
4. **Règles de la base** : Realtime Database → Règles → coller le contenu de `database.rules.json` → Publier.
   Les chemins `shots`, `notes` (app shotlist) et `detente` (app Détente) restent ouverts comme avant ; les données DDC Breakdown sont sous `ddc/…` et celles de UP Slatebook sous `up/…`, chacune réservée à sa propre équipe.

## Équipe

L'administrateur (`adminEmail` dans `config.js`) ajoute les adresses e-mail des membres (Gmail ou autre) depuis le menu du compte → **Équipe**. Une personne non autorisée qui se connecte envoie automatiquement une demande d'accès : badge rouge sur l'avatar de l'administrateur, à accepter ou refuser dans **Équipe**.

Chaque membre a un rôle : **Lecteur** (consulte et exporte), **Commentateur** (consulte et commente), **Éditeur** (modifie tout). Seul l'administrateur supprime un projet. Les rôles sont appliqués par l'app et par les règles de la base (`tools/rules.py` génère `database.rules.json`).

## IA

L'administrateur enregistre une clé API Anthropic pour toute l'équipe : menu du compte → **Clé API de l'équipe**. Elle est stockée dans Firebase (`up/secrets`), lisible seulement par les membres connectés, et n'est jamais dans le code. Pour la changer, même menu. Le modèle est réglable dans `config.js`.

## Fichiers

| Fichier | Rôle |
|---|---|
| `index.html` | l'application |
| `adapter.js` | branchement Firebase (données, comptes, présence), API Anthropic, écrans de connexion et d'équipe |
| `sw.js` | service worker : ouverture de l'app sans réseau |
| `config.js` | configuration Firebase, administrateur, modèle |
| `database.rules.json` | règles de sécurité de la Realtime Database |
