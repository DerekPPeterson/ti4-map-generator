#include <iostream>
#include <fstream>
#include <list>
#include <map>
#include <vector>
#include <algorithm>
#include <cstdlib>
#include <time.h>
#include <exception>

#include "json.hpp"

#define BACKWARD_HAS_BFD 1
#include "backward-cpp/backward.hpp"

using json = nlohmann::json;

using namespace std;

enum PlanetTrait
{
    NO_TRAIT,
    CULTURAL,
    INDUSTRIAL,
    HAZARDOUS
};

map<string, PlanetTrait> trait_key = {
    {"NO_TRAIT", NO_TRAIT},
    {"CULTURAL", CULTURAL},
    {"HAZARDOUS", HAZARDOUS},
    {"INDUSTRIAL", INDUSTRIAL}
};

enum TechColor
{
    NO_COLOR,
    BLUE,
    RED,
    GREEN,
    YELLOW
};

map<string, TechColor> tech_key = {
    {"NO_TECH", NO_COLOR},
    {"BLUE", BLUE},
    {"RED", RED},
    {"GREEN", GREEN},
    {"YELLOW", YELLOW}
};

enum Wormhole
{
    NO_WORMHOLE,
    ALPHA,
    BETA,
    DELTA
};

map<string, Wormhole> wormhole_key = {
    {"NO_WORMHOLE", NO_WORMHOLE},
    {"ALPHA", ALPHA},
    {"BETA", BETA},
    {"DELTA", DELTA}
};

enum Anomaly
{
    NO_ANOMALY,
    EMPTY,
    GRAVITY_RIFT,
    NEBULA,
    SUPERNOVA,
    ASTEROID_FIELD
};

map<string, Anomaly> anomaly_key = {
    {"NO_ANOMALY", NO_ANOMALY},
    {"EMPTY", EMPTY},
    {"GRAVITY_RIFT", GRAVITY_RIFT},
    {"NEBULA", NEBULA},
    {"SUPERNOVA", SUPERNOVA},
    {"ASTEROID_FIELD", ASTEROID_FIELD},
};

typedef struct Planet
{
    string name;
    int resources;
    int influence;
    PlanetTrait trait;
    TechColor tech;
} Planet;

class Tile
{
    int number;
    Wormhole wormhole;
    list<Planet> planets;
    Anomaly anomaly;

    public:
    Tile(int, list<Planet>, Wormhole, Anomaly);
    string get_description_string() const;
};

string Tile::get_description_string() const {
    ostringstream desc;
    desc << "Tile " << number << " - ";
    for (auto it = planets.begin(); it != planets.end(); it++) {
        if (it != planets.begin()) {
            desc << ", ";
        }
        desc << it->name;
    }

    return desc.str();
}

std::ostream& operator<< (std::ostream &out, Tile const& tile) {
    out << tile.get_description_string();
    return out;
}

Tile::Tile(int n, list<Planet> p, Wormhole w, Anomaly a)
{
    number = n;
    planets = p;
    wormhole = w;
    anomaly = a;
}


class Galaxy
{
    list<Tile> tiles;
    Tile *grid[7][7]; // Locations of tiles

    void import_tiles(string tile_filename);

    public:
    Galaxy(string tile_filename);
};

Galaxy::Galaxy(string tile_filename)
{
    import_tiles(tile_filename);
}

Planet create_planet_from_json(json j)
{
    Planet new_planet;

    new_planet.name = j["name"];
    new_planet.resources = j["resources"];
    new_planet.influence = j["influence"];

    new_planet.trait = trait_key.at(j["trait"]);
    new_planet.tech = tech_key.at(j["tech"]);

    return new_planet;
}

Tile create_tile_from_json(json j)
{
    int number = j["number"];
    Wormhole wormhole = wormhole_key.at(j["wormhole"]);
    Anomaly anomaly = anomaly_key.at(j["anomaly"]);

    // Create planet list
    json planet_list = j["planets"];
    list<Planet> planets;
    for (json::iterator it = planet_list.begin(); it != planet_list.end(); it++) {
        planets.push_back(create_planet_from_json(it.value()));
    }

    Tile new_tile = Tile(number, planets, wormhole, anomaly);
    cerr << new_tile << endl;
    return new_tile;
}

void Galaxy::import_tiles(string tile_filename)
{
    // Parse tile json
    // TODO error handle parse errors file not exist etc
    json tile_json;
    ifstream json_file;
    cerr << "Importing tiles from " << tile_filename << endl;
    json_file.open(tile_filename);
    try {json_file >> tile_json;} 
    catch (...) {
        cerr << "Error loading/parsing " << tile_filename << endl;
        exit(-1);
    }
    json_file.close();

    // Create list of tiles
    json tile_list = tile_json["tiles"];
    for (json::iterator it = tile_list.begin(); it != tile_list.end(); it++) {
        tiles.push_back(create_tile_from_json(it.value()));
    }
    cerr << "Loaded " << tiles.size() << " tiles" << endl;
}

int main() {

    srand(time(NULL));

    Galaxy galaxy("tiles.json");

    return 0;
}
