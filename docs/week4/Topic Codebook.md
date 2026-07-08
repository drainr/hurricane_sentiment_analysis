# Topic Codebook

A label and category for every BERTopic topic. The nine project categories: gratitude, preparedness, forecast analysis, evacuation logistics, political / FEMA criticism, misinformation, government resources, personal experience, emotional response. Outlier and short rows are marked excluded. **Note (advisor decision 2026-06-29): "misinformation" is retained as a category slot for the chi-square (it is an all-zero row — no BERTopic topic landed there), but it is NOT reported as a standalone category in H6/H7.** Misinformation content is captured within `political / FEMA criticism` (Reddit) and `misinformation removal` (WH). See the misinformation note below and `decision_log.md`.

WH comment threads also carry four WH-specific categories, added 2026-06-26 per advisor request so H7 can measure each rate instead of lumping them into political/FEMA: `subreddit moderation removal`, `misinformation removal`, `Georgia moderator incident`, `reaction to government Reddit presence`. WH comments only (see block below).

## Reconciled cross-source view (joint deliverable)

Every source's topics grouped into the nine categories, so the same idea gets the same label no matter the platform. Sources: FBp = Facebook posts, FBc = Facebook comments, Rp = Reddit posts, Rc = Reddit comments, WHp = White House posts, WHc = White House comments. The cross-source chi-square runs on these nine categories.

**gratitude** (only on Facebook, basically none on Reddit or WH)

- Gratitude to forecaster [FBc] · Care for forecaster [FBc]

**preparedness**

- Hurricane prep checklist [FBp] · Home prep [FBc, Rc] · Supplies prep [FBc, Rc] · Storm prep and insurance [Rp]

**forecast analysis** (the biggest one, every community source has it)

- Forecast and storm tracking [FBp] · General storm/hurricane discussion [FBc, Rp, Rc] · Cone and track [FBc, Rc] · Eye and eyewall [FBc, Rc] · Storm surge [FBc, Rp, Rc] · Storm intensity [FBc, Rc] · Landfall timing [FBc, Rc] · Track direction [FBc, Rc] · Gulf conditions [FBc, Rc] · Tornado concern [FBc, Rc] · Storm speed [FBc] · Models/recon/data sources [Rc] · Wind and shear [Rc] · Weather sources and sites [Rp] · Automated forecast observations [Rp]

**evacuation logistics**

- Evacuation [FBc, Rp, Rc] · Driving and traffic [Rc] · Pet evacuation and shelter [Rp]

**political / FEMA criticism** (Reddit and WH, barely any on Facebook)

- FEMA and political reaction [Rp, Rc, WHc] · Politics and partisan reaction [Rc] · Climate change debate [Rc]

**misinformation** — nothing landed here. **Per advisor decision 2026-06-29, misinformation is NOT a standalone topic category.** BERTopic never split off a misinfo cluster because misinfo is a cross-cutting stance that rides on other topics (FEMA aid, politics, weather), not a topic of its own. It is captured inside `political / FEMA criticism` on Reddit and inside the WH-only `misinformation removal` category on White House comments. H6 and H7 therefore refer to political / FEMA-critical discourse rather than a "misinformation" category. (Not the same as `misinformation removal` below — that's mod notices saying misinfo got taken down, not the stance itself.) See `decision_log.md` (2026-06-29).

**White House–specific (H7 only)** — WH comments only:

- Moderation and trolling [WHc] → `subreddit moderation removal`
- Misinfo-removal notices [WHc] → `misinformation removal`
- Which subreddit posted [WHc] → `reaction to government Reddit presence`
- Georgia mods removed link [WHc] → `Georgia moderator incident`

The cross-source chi-square still uses the nine shared categories — these four only matter for the H7 cut (within WH, and WH vs organic Reddit), since Facebook and Reddit have none of them.

**government resources**

- WH storm-response updates [WHp] · FEMA assistance and aid [Rp] · Tornado warning alert [FBp]

**personal experience**

- Location-specific impact [FBc, Rc] · Travel and plans impact [FBc, Rp, Rc] · Power outages [FBc, Rp, Rc] · Flooding experience [FBc, Rc] · Local weather conditions [FBc, Rc] · Past-hurricane comparison [FBc, Rc] · Pets during storm [FBc, Rc] · School and campus impact [FBc, Rc] · Insurance [Rc] · Storm damage – trees [Rc] · Communications/cell service [Rc] · Watching the broadcast / weather media [FBc, Rc] · Relocation chatter [Rc] · Heat and weather chatter [Rc]

**emotional response** (mostly Facebook, Phillips's audience)

- Prayers and faith / well-wishes [FBc] · Stay safe [FBc] · Rule 7 reassurance [FBc] · Reassurance and trust [FBc] · Community / storm-name banter [FBc] · General questions [FBc] · Hurricane season / general storm chatter [Rc]

### Reconciliation notes

- Checked that every label maps to exactly one category across all six files.
- The alignments the plan cares about hold up: Reddit and Facebook "Evacuation" both go to `evacuation logistics`, and Reddit's model/track talk lines up with Facebook's "Forecast and storm tracking" under `forecast analysis`.
- Status: final. Reconciled labels reviewed and signed off by Angelo.

### Decisions

1. **Misinformation**: folded into `political / FEMA criticism` for now. No separate misinfo topic or flag yet, asking the advisor (see open questions). H6 and H7 name it.
2. **FB tornado-alert posts (topics 1–9)**: `government resources`.
3. **Outliers (-1)**: leave them excluded, report the rate, same way for all six files. No reduce_outliers.
4. **WH comment categories (2026-06-26, per advisor)**: broke WHc topics 1–4 out of the political/FEMA + excluded buckets into their own categories (see the WH-specific block above) so H7 can compare their rates. Same day, removed the 5 WH posts + 973 WH comments that the keyword search had pulled into the Reddit files (they already live in the WH files); master rebuilt to 187,359 rows, both guardrails passing.

---

## Facebook posts

| Topic          | Top words                 | Label                       | Category             |
| -------------- | ------------------------- | --------------------------- | -------------------- |
| 0              | storm, winds, track       | Forecast and storm tracking | forecast analysis    |
| 1              | area, stay tuned, station | Tornado warning alert       | government resources |
| 2              | weather, latest, app      | Tornado warning alert       | government resources |
| 3              | tuned, updates, station   | Tornado warning alert       | government resources |
| 4              | DeSoto county             | Tornado warning alert       | government resources |
| 5              | Polk county               | Tornado warning alert       | government resources |
| 6              | Hardee county             | Tornado warning alert       | government resources |
| 7              | Highlands county          | Tornado warning alert       | government resources |
| 8              | Manatee county            | Tornado warning alert       | government resources |
| 9              | Sarasota county           | Tornado warning alert       | government resources |
| 10             | water, store, clean       | Hurricane prep checklist    | preparedness         |
| -1             | outlier                   | Outlier                     | excluded             |
| excluded_short | short                     | Too short                   | excluded             |

## Facebook comments

| Topic          | Top words                   | Label                     | Category             |
| -------------- | --------------------------- | ------------------------- | -------------------- |
| 0              | hurricane, storm, weather   | General storm discussion  | forecast analysis    |
| 1              | orlando, flight, flying     | Travel and plans impact   | personal experience  |
| 2              | rain, wind, gusts           | Local weather conditions  | personal experience  |
| 3              | surge, storm surge, tide    | Storm surge questions     | forecast analysis    |
| 4              | zone, evacuation, evacuate  | Evacuation                | evacuation logistics |
| 5              | thank, keeping, updates     | Gratitude to forecaster   | gratitude            |
| 6              | dr pepper, debbie           | Community banter          | emotional response   |
| 7              | wondering, question         | General questions         | emotional response   |
| 8              | cat, landfall, pets         | Storm intensity           | forecast analysis    |
| 9              | beach, st pete, daytona     | Travel and plans impact   | personal experience  |
| 10             | florida, praying, prayers   | Prayers and well-wishes   | emotional response   |
| 11             | tampa, tampa bay            | Location-specific impact  | personal experience  |
| 12             | rule, freak, number         | Rule 7 reassurance        | emotional response   |
| 13             | sarasota, bradenton, siesta | Location-specific impact  | personal experience  |
| 14             | praying, god, jesus         | Prayers and faith         | emotional response   |
| 15             | fsu, students, school       | School and campus impact  | personal experience  |
| 16             | east, north, south, west    | Storm direction questions | forecast analysis    |
| 17             | phillips, denis, thank      | Gratitude to forecaster   | gratitude            |
| 18             | tornado, warning            | Tornado concern           | forecast analysis    |
| 19             | radio, live, abc            | Watching the broadcast    | personal experience  |
| 20             | flooding, flood, water      | Flooding experience       | personal experience  |
| 21             | milton, uncle milton        | Storm-name banter         | emotional response   |
| 22             | power, outages              | Power outages             | personal experience  |
| 23             | wednesday, thursday, time   | Timing questions          | forecast analysis    |
| 24             | denis, thank denis          | Gratitude to forecaster   | gratitude            |
| 25             | helene, surge, storm        | Storm surge and Helene    | forecast analysis    |
| 26             | landfall, make landfall     | Landfall timing           | forecast analysis    |
| 27             | ian, charley, irma          | Past-hurricane comparison | personal experience  |
| 28             | county, polk, hernando      | Location-specific impact  | personal experience  |
| 29             | track, change, update       | Track changes             | forecast analysis    |
| 30             | eye, eyewall                | Eye and eyewall           | forecast analysis    |
| 31             | safe, stay safe, hope       | Stay safe and well-wishes | emotional response   |
| 32             | jesus, god, pray            | Prayers and faith         | emotional response   |
| 33             | denis, freak, follow        | Reassurance and trust     | emotional response   |
| 34             | sleep, rest, thanks         | Care for forecaster       | gratitude            |
| 35             | moving, mph, fast, slow     | Storm speed               | forecast analysis    |
| 36             | roof, windows, shutters     | Home prep                 | preparedness         |
| 37             | water, ice, freezer         | Supplies prep             | preparedness         |
| 38             | dennis, thank dennis        | Gratitude to forecaster   | gratitude            |
| 39             | cone, uncertainty           | Cone of uncertainty       | forecast analysis    |
| 40             | pets, dog, dogs             | Pets during storm         | personal experience  |
| 41             | gulf, warm, waters          | Gulf conditions           | forecast analysis    |
| 42             | pinellas, pinellas park     | Location-specific impact  | personal experience  |
| 43             | debby, ts debby             | Storm-naming chatter      | forecast analysis    |
| -1             | outlier                     | Outlier                   | excluded             |
| excluded_short | short                       | Too short                 | excluded             |

## White House posts

| Topic | Top words              | Label                     | Category             |
| ----- | ---------------------- | ------------------------- | -------------------- |
| 0     | fema, people, response | WH storm-response updates | government resources |

## White House comments

| Topic          | Top words                  | Label                       | Category                               |
| -------------- | -------------------------- | --------------------------- | -------------------------------------- |
| 0              | fema, people, like         | FEMA and political reaction | political / FEMA criticism             |
| 1              | content removed, trolling  | Moderation and trolling     | subreddit moderation removal           |
| 2              | claims, legitimate, backup | Misinfo-removal notices     | misinformation removal                 |
| 3              | florida, subreddit         | Which subreddit posted      | reaction to government Reddit presence |
| 4              | georgia, mods, petty       | Georgia mods removed link   | Georgia moderator incident             |
| -1             | swing states               | Outlier                     | excluded                               |
| excluded_short | short                      | Too short                   | excluded                               |

## Reddit posts

| Topic          | Top words                  | Label                           | Category                   |
| -------------- | -------------------------- | ------------------------------- | -------------------------- |
| 0              | milton, hurricane, florida | General hurricane discussion    | forecast analysis          |
| 1              | helene, hurricane, storm   | General hurricane discussion    | forecast analysis          |
| 2              | insurance, water, storm    | Storm prep and insurance        | preparedness               |
| 3              | zone, evacuate, evacuation | Evacuation                      | evacuation logistics       |
| 4              | weather, live, sites       | Weather sources and sites       | forecast analysis          |
| 5              | flight, orlando, trip      | Travel and plans impact         | personal experience        |
| 6              | help, assistance, fema     | FEMA assistance and aid         | government resources       |
| 7              | power, outage, georgia     | Power outages                   | personal experience        |
| 8              | hurricane, storm, florida  | Storm formation outlook         | forecast analysis          |
| 9              | fema, funding, trump       | FEMA and political reaction     | political / FEMA criticism |
| 10             | surge, storm surge, feet   | Storm surge                     | forecast analysis          |
| 11             | debby, storm debby         | General hurricane discussion    | forecast analysis          |
| 12             | https, gov, observation    | Automated forecast observations | forecast analysis          |
| 13             | shelter, pet, evacuation   | Pet evacuation and shelter      | evacuation logistics       |
| -1             | outlier                    | Outlier                         | excluded                   |
| excluded_short | short                      | Too short                       | excluded                   |

## Reddit comments

| Topic          | Top words                       | Label                           | Category                   |
| -------------- | ------------------------------- | ------------------------------- | -------------------------- |
| 0              | desantis, biden, trump          | Politics and partisan reaction  | political / FEMA criticism |
| 1              | water, gas, food, buy           | Supplies prep                   | preparedness               |
| 2              | cat, landfall, storm            | Storm intensity                 | forecast analysis          |
| 3              | tampa, bay, sarasota            | Location-specific impact        | personal experience        |
| 4              | florida, state, moved           | Relocation chatter              | personal experience        |
| 5              | fema, rep, funding              | FEMA and political reaction     | political / FEMA criticism |
| 6              | evacuate, evacuation, zone      | Evacuation                      | evacuation logistics       |
| 7              | eye, eyewall, ewrc              | Eye and eyewall                 | forecast analysis          |
| 8              | milton, florida, storm          | General hurricane discussion    | forecast analysis          |
| 9              | helene, charley, storm          | Past-hurricane comparison       | personal experience        |
| 10             | insurance, companies            | Insurance                       | personal experience        |
| 11             | hurricane, season, people       | Hurricane season chatter        | emotional response         |
| 12             | pets, dog, animals              | Pets during storm               | personal experience        |
| 13             | surge, storm surge, map         | Storm surge                     | forecast analysis          |
| 14             | cone, nhc, track                | Cone and track                  | forecast analysis          |
| 15             | ryan hall, youtube              | Weather influencers and media   | personal experience        |
| 16             | flood, flooding, water          | Flooding experience             | personal experience        |
| 17             | power, lost power, outages      | Power outages                   | personal experience        |
| 18             | tornado, tornadoes              | Tornado concern                 | forecast analysis          |
| 19             | models, model, forecast         | Model and forecast talk         | forecast analysis          |
| 20             | roof, windows, concrete         | Home prep                       | preparedness               |
| 21             | pressure, mb, recon             | Pressure and recon              | forecast analysis          |
| 22             | wind, shear, mph                | Wind and shear                  | forecast analysis          |
| 23             | storm, storms, like             | General storm chatter           | emotional response         |
| 24             | gfs, icon, models               | Model and forecast talk         | forecast analysis          |
| 25             | asheville, road, nc             | Location-specific impact        | personal experience        |
| 26             | noaa, recon, tropicaltidbits    | Data sources                    | forecast analysis          |
| 27             | climate, climate change         | Climate change debate           | political / FEMA criticism |
| 28             | driving, car, traffic           | Driving and traffic             | evacuation logistics       |
| 29             | landfall, hours, make landfall  | Landfall timing                 | forecast analysis          |
| 30             | east, north, south, shift       | Track direction                 | forecast analysis          |
| 31             | trees, tree, oak                | Storm damage (trees)            | personal experience        |
| 32             | hours, days, tomorrow           | Timing updates                  | forecast analysis          |
| 33             | power, georgia power, pay       | Power and utility bills         | personal experience        |
| 34             | orlando, hotel, flooding        | Location-specific impact        | personal experience        |
| 35             | flight, airport, cancelled      | Travel and plans impact         | personal experience        |
| 36             | summer, heat, humidity          | Heat and weather chatter        | personal experience        |
| 37             | gulf, mexico, warm              | Gulf conditions                 | forecast analysis          |
| 38             | rain, wind, raining             | Local weather conditions        | personal experience        |
| 39             | katrina, new orleans            | Past-hurricane comparison       | personal experience        |
| 40             | nhc, forecast, models           | Model and forecast talk         | forecast analysis          |
| 41             | weather channel, meteorologists | Weather influencers and media   | personal experience        |
| 42             | yucatan, mexico, cancun         | Storm location and track        | forecast analysis          |
| 43             | school, schools, closed         | School and campus impact        | personal experience        |
| 44             | cell, service, satellite        | Communications and cell service | personal experience        |
| 45             | leave, stay, leaving            | Evacuation                      | evacuation logistics       |
| -1             | outlier                         | Outlier                         | excluded                   |
| excluded_short | short                           | Too short                       | excluded                   |
