package com.restaurant.ai.repository;

import com.restaurant.ai.model.InventoryPrediction;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;

/**
 * Spring Data JPA Repository for InventoryPrediction entities.
 * Provides CRUD operations and custom queries for waste optimization results.
 */
@Repository
public interface InventoryPredictionRepository extends JpaRepository<InventoryPrediction, Integer> {

    /**
     * Find all inventory predictions for a specific date.
     */
    List<InventoryPrediction> findByPredictionDate(LocalDate predictionDate);

    /**
     * Find all predictions for a specific inventory item by name.
     */
    List<InventoryPrediction> findByInventoryItemName(String inventoryItemName);

    /**
     * Find predictions for a specific item within a date range.
     */
    List<InventoryPrediction> findByInventoryItemNameAndPredictionDateBetween(
            String inventoryItemName, LocalDate startDate, LocalDate endDate);

    /**
     * Find all predictions within a date range.
     */
    List<InventoryPrediction> findByPredictionDateBetween(LocalDate startDate, LocalDate endDate);

    /**
     * Find predictions where the recommended action matches a specific value.
     * Useful for filtering items that need attention (e.g., "Reduce Reorder Level").
     */
    List<InventoryPrediction> findByActionRecommended(String actionRecommended);
}
