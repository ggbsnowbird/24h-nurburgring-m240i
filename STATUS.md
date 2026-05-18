# Project Status - M240i Data Pipeline

## Objectif du projet
Construire une base de donnees rapide et propre a partir de la source PDF locale des `Sector Times Race`, en ne conservant que la classe `BMW M240i Racing Cup`, puis enrichir avec l'heure de la journee (`lap day time`) issue de LiveTiming — afin de produire le mapping final: `driver_name + lap_no -> heure du tour`.

## Source imposee
- PDF local: `Data Source/42_24h_Race_Sector_Times.pdf`
- Source complementaire: `https://livetiming.azurewebsites.net/event/50/laps-data?session=4600205102&startingNo=XXX`

## Etat: DONE

### Base SQLite: `m240i_sector_times.db`

| Table | Contenu | Lignes |
|---|---|---|
| `cars` | Metadonnees voiture / equipage / best time | 11 |
| `laps` | Tours PDF (lap_no, driver_no, laptime, 9 secteurs, 8 vitesses) | 1147 |
| `live_timing_laps` | Heure du tour LiveTiming (lap_day_time UTC) | 1147 |
| `lap_driver_times` | Vue finale: driver_name + lap_no + heure du tour | - |

### Voitures M240i
`195, 650, 651, 652, 653, 658, 665, 667, 669, 670, 677`

### Couverture
100% — chaque tour PDF a son heure de la journee LiveTiming.

### Vue requetable
```sql
SELECT car_no, lap_no, driver_no, driver_name, lap_time_pdf, lap_day_time
FROM lap_driver_times
WHERE car_no = 652
ORDER BY lap_no;
```

## Definition de done - ATTEINTE
1. Tours PDF en base: OK
2. Heure du tour LiveTiming: OK
3. Mapping `car_no + lap_no + driver_name -> lap_day_time`: OK
