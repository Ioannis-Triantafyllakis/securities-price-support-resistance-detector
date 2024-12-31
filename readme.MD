### A minimal web app tool to instantly detect support & resistance levels for a 140.000+ stocks!

Finding the support & resistance levels of a security's price is crucial when looking for entrance or exit opportunities, but can be cumbersome and time-consuming. </br>
I automated the process with Python and streamlit, and now i get them in seconds.</br>
</br>
The support and resistance levels are calculated based on the fractals' method.
</br>
</br>
The user can either get all the support & resistance levels of a stock for a specific timeframe, as below:
</br>
</br>
![Main screen](https://github.com/Ioannis-Triantafyllakis/securities-price-support-resistance-detector/blob/development/media/Main_screen.PNG)
</br>
</br>
or they can get only the global support and resistance level of the timeframe they choose, as seen below:
</br>
</br>
![Main screen](media\Main_screen_global_levels.PNG)
</br>
</br>
Other features:
* A scrollable bar element below the diagram allows the user to zoom-in and out.
* Expandable graph, so larger timeframes yield more visible graphs.
* An API integrator (TwelveData API is used to extract historical data of securities).
* Pre-commit hooks that help us check code linting and formatting before commiting.
