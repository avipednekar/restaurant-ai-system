package com.restaurant.ai.service;

import com.restaurant.ai.model.DemandPrediction;
import com.restaurant.ai.model.InventoryPrediction;
import com.restaurant.ai.repository.DemandPredictionRepository;
import com.restaurant.ai.repository.InventoryPredictionRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDate;
import java.util.List;

/**
 * Service layer for retrieving ML predictive analytics data.
 */
@Service
@RequiredArgsConstructor
public class AnalyticsService {

    private final DemandPredictionRepository demandPredictionRepository;
    private final InventoryPredictionRepository inventoryPredictionRepository;

    /**
     * Get demand predictions for a specific date.
     */
    public List<DemandPrediction> getDemandPredictionsByDate(LocalDate date) {
        return demandPredictionRepository.findByPredictionDate(date);
    }

    /**
     * Get demand predictions within a date range.
     */
    public List<DemandPrediction> getDemandPredictionsByDateRange(LocalDate startDate, LocalDate endDate) {
        return demandPredictionRepository.findByPredictionDateBetween(startDate, endDate);
    }

    /**
     * Get demand predictions for a specific menu item.
     */
    public List<DemandPrediction> getDemandPredictionsByMenuItem(Integer menuItemId) {
        return demandPredictionRepository.findByMenuItemId(menuItemId);
    }

    /**
     * Get inventory waste predictions for a specific date.
     */
    public List<InventoryPrediction> getInventoryPredictionsByDate(LocalDate date) {
        return inventoryPredictionRepository.findByPredictionDate(date);
    }

    /**
     * Get inventory waste predictions within a date range.
     */
    public List<InventoryPrediction> getInventoryPredictionsByDateRange(LocalDate startDate, LocalDate endDate) {
        return inventoryPredictionRepository.findByPredictionDateBetween(startDate, endDate);
    }

    /**
     * Get inventory predictions flagged with a specific action (e.g., "Reduce Reorder Level").
     */
    public List<InventoryPrediction> getInventoryPredictionsByAction(String action) {
        return inventoryPredictionRepository.findByActionRecommended(action);
    }
}
