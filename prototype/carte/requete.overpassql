[out:json][timeout:90];
(
  relation["boundary"="administrative"]["admin_level"="8"]["name"~"^(Aubagne|La Penne-sur-Huveaune)$"];
  relation["boundary"="administrative"]["name"="La Valentine"](43.28,5.44,43.34,5.53);
);
out geom;
node["place"~"^(suburb|quarter|neighbourhood|hamlet|locality|village|isolated_dwelling)$"](43.23,5.45,43.35,5.66);
out;
