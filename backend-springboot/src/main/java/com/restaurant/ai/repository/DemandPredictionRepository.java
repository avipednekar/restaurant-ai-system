package com.restaurant.ai.repository;

import com.restaurant.ai.model.DemandPrediction;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;

/**
 * Spring Data JPA Repository for DemandPrediction entities.
 * Provides CRUD operations and custom queries for demand forecasting results.
 */
@Repository
public interface DemandPredictionRepository extends JpaRepository<DemandPrediction, Integer> {

    /**
     * Find all demand predictions for a specific date.
     */
    List<DemandPrediction> findByPredictionDate(LocalDate predictionDate);

    /**
     * Find all demand predictions for a specific menu item.
     */
    List<DemandPrediction> findByMenuItemId(Integer menuItemId);

    /**
     * Find predictions for a menu item within a date range.
     */
    List<DemandPrediction> findByMenuItemIdAndPredictionDateBetween(
            Integer menuItemId, LocalDate startDate, LocalDate endDate);

    /**
     * Find all predictions for a given date range.
     */
    List<DemandPrediction> findByPredictionDateBetween(LocalDate startDate, LocalDate endDate);

    /**
     * Find predictions by model name.
     */
    List<DemandPrediction> findByModelName(String modelName);
}
