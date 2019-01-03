# pelias-qgis-plugin

**Note, only QGIS v3.x is supported.**

Set of tools to use hosted [Pelias](https://github.com/pelias/pelias) API's within QGIS from configurable sources.

Pelias Geocoding gives you easy access to the following API's:

- [Search](https://github.com/pelias/documentation/blob/master/search.md)
- [Structured Search](https://github.com/pelias/documentation/blob/master/structured-geocoding.md)
- [Reverse Geocoding](https://github.com/pelias/documentation/blob/master/reverse.md)

In case of issues/bugs, please use the [issue tracker](https://github.com/nilsnolde/pelias-qgis-plugin/issues).

The plugin gives access to an open-source project, which has tons of useful [documentation](https://github.com/pelias/documentation) on all Pelias topics.

2 Pelias API providers with global coverage are pre-configured in the plugin:

- [geocode.earth](https://geocode.earth), commercial solution from two Pelias maintainers
- [openrouteservice](https://openrouteservice.org), a GIScience group from University of Heidelberg

## Functionalities

### General

Use QGIS to generate input for **forward geocoding** and **reverse geocoding**.

The menu entry is located in *Web* menu (will be auto-created if you don't have it yet) and it exposes a Pelias toolbar by default with 3 buttons:

- **Pelias Controls**: complete GUI for interactive advanced geocoding from map canvas or batch operations using processing algorithms

- **Quick Forward Geocode**: just enter an address and forward geocoding is performed using default parameters

- **Quick Reverse Geocode**: click the map on your point of interest and reverse geocoding is performed using default parameters

Additionally, you'll find a Pelias Processing group in the Processing Toolbox for background batch operations.

### Customization

You can configure Pelias providers from the menu (*Web* ► *Pelias Geooding* ► *Provider configuration*) or from the config button in **Pelias Control** GUI.

These provider settings are exposed in every Pelias Geocoding tool and are centrally managed.

[geocode.earth](https://geocode.earth) and [openrouteservice](https://openrouteservice.org) are pre-configured as providers. However, you'll have to get your hands on API keys to use either provider:

- geocode.earth: request an invite on [geocode.earth](https://geocode.earth) for a trial
- openrouteservice: [sign up](https://openrouteservice.org/sign-up) and create a API key in your dashboard

Additionally you can register other providers, like `localhost`. If you register a provider who doesn't require an API key or doesn't have request limit (like `localhost usually would), just leave those fields empty or 0.

## Getting Started

### Prerequisites

QGIS version: min. **v3.0**

API key from a provider.

### Installation

Either from QGIS plugin repository. Or if you want to install the latest developmeent release manually:
  - [Download](https://github.com/nilsnolde/pelias-qgis-plugin/archive/development.zip) ZIP file from Github
  - Unzip folder contents and copy `PeliasGeocoding` folder to:
    - Linux: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins`
    - Windows: `C:\Users\USER\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins`
    - Mac OS: `Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins`
