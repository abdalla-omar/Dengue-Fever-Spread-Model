#ifndef DENGUE_COUPLED_HPP
#define DENGUE_COUPLED_HPP

#include <cadmium/modeling/celldevs/asymm/config.hpp>    // AsymmCellConfig
#include <cadmium/modeling/celldevs/asymm/coupled.hpp>
#include "dengue_cell.hpp"

using namespace cadmium::celldevs;

/// Factory for the AsymmCellDEVSCoupled<DengueState,double>
inline std::shared_ptr<AsymmCell<DengueState,double>>
addDengueCell(
  const std::string& cellId,
  const std::shared_ptr<const AsymmCellConfig<DengueState,double>>& config
) {
    if(config->cellModel == "DengueCell") {
        return std::make_shared<DengueCell>(cellId, config);
    } else {
        throw std::bad_typeid();
    }
}

#endif // DENGUE_COUPLED_HPP
