#ifndef DENGUE_COUPLED_HPP
#define DENGUE_COUPLED_HPP

#include <cadmium/modeling/celldevs/asymm/coupled.hpp>
#include <nlohmann/json.hpp>
#include <memory>
#include "dengue_cell.hpp"

using namespace cadmium::celldevs;
using namespace std;

// alias for the asymmetric coupled
using DengueCoupled = AsymmCellDEVSCoupled<DengueState,double>;

// factory signature matches AsymmCellDEVSCoupled: (string id, config)
inline shared_ptr<AsymmCell<DengueState,double>> addDengueCell(
    const string& cellId,
    const shared_ptr<const AsymmCellConfig<DengueState,double>>& cfg)
{
    if (cfg->cellModel == "DengueCell") {
        return make_shared<DengueCell>(cellId, cfg);
    } else {
        throw runtime_error("Unknown model: "+cfg->cellModel);
    }
}

// Top‐level coupled: reads the JSON “cells” object directly
struct DengueModel : public DengueCoupled {
    DengueModel(string const& id, string const& jsonConfigPath)
      : DengueCoupled(id, addDengueCell, jsonConfigPath)
    {}
};

#endif // DENGUE_COUPLED_HPP
