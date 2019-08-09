# SnmpNetworkTopologyVisualizator

This is a visualization software that uses python backend scripts to collect SNMP information about hosts (configured in config.ini) and create a frontend interactive map that produces a network topology using D3 JavaScript library and PlotLy traffic graphs for each interface it founds. 

## [Example visualized network link to networkgeekstuff.com](https://networkgeekstuff.com/article_upload/visualize/snmp_full/)

## Usage
To use this software, simply adjust config.ini with SNMP configuration for your devices, optionally also check pyconfig.py for low level configuration. THen have network_mapper.py script executed every X minutes by some scheduler like cron and your will start getting a network topology map in the html directory that you can simply open with your browser

## About
Software produced as experimental for my work and published together with article on networkgeekstuff.com

### Disclaimer, this software is available "as is" with no warranty. Use at your own risk
