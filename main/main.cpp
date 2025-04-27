#include <cadmium/modeling/celldevs/asymm/coupled.hpp>
#include <cadmium/simulation/logger/csv.hpp>
#include <cadmium/simulation/root_coordinator.hpp>
#include <nlohmann/json.hpp>
#include <iostream>
#include "include/dengue_coupled.hpp"

using namespace cadmium::celldevs;
using namespace cadmium;
using namespace std;

int main(int argc, char** argv) {
    if (argc < 2) {
        cout<<"Usage: "<<argv[0]<<" dengue_config.json [sim_time]\n";
        return 1;
    }
    string cfg = argv[1];
    double simTime = (argc>2)? stod(argv[2]) : 1000.0;

    auto model = make_shared<DengueModel>("DengueSim", cfg);
    model->buildModel();

    RootCoordinator root(model);
    root.setLogger<CSVLogger>("dengue_output.csv", ";");
    root.start();
    root.simulate(simTime);
    root.stop();

    return 0;
}
