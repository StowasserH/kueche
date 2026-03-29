# Kueche
Kueche is a media player for Raspery-Pis with touchscreen. It is based on the Lcars interface known from StarTreck(tm).

<img src="pictures/dash.png" alt="Dashboard" width="400">

The following is thus possible:
  * Listen to various internet radio stations.
  * Select and play music files on a data medium

The name Kueche comes from the German word 'Küche' as this radio is operated by being in my kitchen.

## Getting Started

This project uses modern Python packaging with `pyproject.toml`. You'll need Python 3.8 or higher.

### Prerequisites

On Debian/Ubuntu-based systems:
```bash
sudo apt-get update
sudo apt-get -y upgrade
sudo apt-get install python3 python3-pip python3-dev portaudio19-dev libmpv-dev \
                     python3-alsaaudio git build-essential libsasl2-dev libldap2-dev \
                     libssl-dev libxml2-dev libxmlsec1-dev pkg-config qtbase5-dev
```

### Installation

1. **Clone repositories**:
```bash
git clone https://github.com/StowasserH/kueche.git
git clone https://github.com/StowasserH/pylcars.git

cd kueche
```

2. **Install dependencies**:
```bash
# Create virtual environment (recommended)
python3 -m venv .venv
source .venv/bin/activate

# Upgrade pip, setuptools, wheel
pip install --upgrade pip setuptools wheel

# Install pylcars first
pip install ../pylcars

# Install kueche and dependencies
pip install -e .
```

3. **Run the application**:
```bash
# Option 1: Using the run wrapper
python3 run_kueche.py

# Option 2: Using installed command
kueche

# Option 3: As a Python module
python3 -m kueche
```


## Configuration

Please create a config.ini as follows. Then you can adjust the values in the file according to your needs:
```
cp config.ini_skeleton config.ini
```

### Sounds and fonts
For copyright reasons, the fonts and sounds folders are empty. However, there are many sound effects from the movies available on the internet that you can use.
You can also find beautiful fonts that match the movies.

### Calendar
If you want to use the Google calendar you have to get an oauth2 client_id for your account there.
Then your appointments can be displayed with the calendar_id.

## Development

Feel free to use and modify it, but please help me to improve it.

### Coding style

If you commit code pls try to format it in [PEP8](https://www.python.org/dev/peps/pep-0008/)


## Authors

* **Harald Stowasser** - *Initial work* - [StowasserH](https://github.com/StowasserH)

See also the list of [contributors](https://github.com/StowasserH/pylcars/contributors) who participated in this project.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details
