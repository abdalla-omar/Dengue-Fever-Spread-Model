#include <nlohmann/json.hpp>
#include <cadmium/modeling/celldevs/asymm/coupled.hpp>
#include <cadmium/simulation/logger/csv.hpp>
#include <cadmium/simulation/root_coordinator.hpp>

#include "dengue_state.hpp"
#include "dengue_cell.hpp"
#include "dengue_coupled.hpp"

using namespace cadmium::celldevs;
using namespace cadmium;

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "Usage: " << argv[0]
                  << " <asymm_config.json> [sim_time (default 100)]\n";
        return 1;
    }
    const std::string configFile = argv[1];
    // default to 365 days instead of 100
    double simTime = (argc > 2) ? std::stod(argv[2]) : 365.0;
	
    // build the asymmetric coupled model
    auto model = std::make_shared<AsymmCellDEVSCoupled<DengueState,double>>(
        "DengueModel",    // model ID for logging
        addDengueCell,    // factory
        configFile        // JSON config path
    );
    model->buildModel();

    // simulate with CSV logger
    RootCoordinator root(model);
    root.setLogger<CSVLogger>("dengue_log.csv",";");
    root.start();
    root.simulate(simTime);
    root.stop();
    return 0;
}
