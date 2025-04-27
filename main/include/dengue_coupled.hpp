#ifndef DENGUE_COUPLED_HPP
#define DENGUE_COUPLED_HPP

#include <cadmium/modeling/celldevs/grid/coupled.hpp> 
#include <nlohmann/json.hpp>
#include <memory>
#include "dengue_cell.hpp"

using namespace cadmium::celldevs;
using namespace std;

// Use the grid‐coupled model
using DengueCoupled = GridCellDEVSCoupled<DengueState,double>;

// Factory signature now matches GridCellDEVSCoupled
inline shared_ptr<GridCell<DengueState,double>> addDengueCell(
    const vector<int>& cellId,
    const shared_ptr<const GridCellConfig<DengueState,double>>& cfg
) {
    if (cfg->cellModel == "DengueCell") {
        return make_shared<DengueCell>(cellId, cfg);
    } else {
        throw runtime_error("Unknown cellModel: " + cfg->cellModel);
    }
}

struct DengueModel : public DengueCoupled {
    DengueModel(const string& id, const string& jsonConfigPath)
      : DengueCoupled(id, addDengueCell, jsonConfigPath) {}
};

#endif // DENGUE_COUPLED_HPP
