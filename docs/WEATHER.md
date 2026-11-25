# Weather layer

The prototype currently accepts manually entered weather values and stores them only in the UI session for demonstration. The `WeatherSnapshot` structure defines a future provider-neutral interface. No API, forecast, station, satellite, or reanalysis feed is connected.

Before deployment: select a source; confirm licensing and geographic coverage; retain source/time/units; validate missingness, freshness and ranges; test timezone handling; and display provenance and uncertainty. Do not use these demo values to make operational farm decisions.
