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
    CULTURAL,
    INDUSTRIAL,
    HAZARDOUS
};

map<string, PlanetTrait> trait_key = {
    {"CLUTURAL", CULTURAL},
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
    {"NONE", NO_COLOR},
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

    public:
    Tile(int, list<Planet>, Wormhole);
};

Tile::Tile(int n, list<Planet> p, Wormhole w)
{
    number = n;
    planets = p;
    wormhole = w;
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

    new_planet.trait = trait_key[j["trait"]];
    new_planet.tech = tech_key[j["tech"]];

    return new_planet;
}

void Galaxy::import_tiles(string tile_filename)
{
    // Parse tile json
    // TODO error handle parse errors file not exist etc
    json tile_json;
    ifstream json_file;
    json_file.open(tile_filename);
    json_file >> tile_json;
    json_file.close();

    // Create list of tiles
    json tile_list = tile_json["tiles"];
    for (json::iterator it = tile_list.begin(); it != tile_list.end(); it++) {
        json planet_list = it.value()["planets"];
        list<Planet> planets;
        for (json::iterator it = planet_list.begin(); it != planet_list.end(); it++) {
            planets.push_back(create_planet_from_json(it.value()));
        }
        int number = it.value()["number"];
        Wormhole wormhole = wormhole_key[it.value()["wormhole"]];
        Tile new_tile = Tile(number, planets, wormhole);

        tiles.push_back(new_tile);
    }
}

int main() {

    srand(time(NULL));

    Galaxy galaxy("tiles.json");

    return 0;
}
