package com.restaurant.ai.controller;

import com.restaurant.ai.model.DemandPrediction;
import com.restaurant.ai.model.InventoryPrediction;
import com.restaurant.ai.service.AnalyticsService;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;

/**
 * REST Controller for ML predictive analytics.
 * Exposes demand forecasting and inventory waste predictions to the dashboard.
 */
@RestController
@RequestMapping("/api/analytics")
@RequiredArgsConstructor
public class AnalyticsController {

    private final AnalyticsService analyticsService;

    // ===================== DEMAND PREDICTIONS =====================

    /**
     * GET /api/analytics/demand?date=2026-05-29
     * Fetch demand predictions for a specific date.
     */
    @GetMapping("/demand")
    public ResponseEntity<List<DemandPrediction>> getDemandPredictionsByDate(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date) {
        return ResponseEntity.ok(analyticsService.getDemandPredictionsByDate(date));
    }

    /**
     * GET /api/analytics/demand/range?startDate=2026-05-01&endDate=2026-05-31
     * Fetch demand predictions within a date range.
     */
    @GetMapping("/demand/range")
    public ResponseEntity<List<DemandPrediction>> getDemandPredictionsByDateRange(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate) {
        return ResponseEntity.ok(analyticsService.getDemandPredictionsByDateRange(startDate, endDate));
    }

    /**
     * GET /api/analytics/demand/item/{menuItemId}
     * Fetch demand predictions for a specific menu item.
     */
    @GetMapping("/demand/item/{menuItemId}")
    public ResponseEntity<List<DemandPrediction>> getDemandPredictionsByMenuItem(
            @PathVariable Integer menuItemId) {
        return ResponseEntity.ok(analyticsService.getDemandPredictionsByMenuItem(menuItemId));
    }

    // ===================== INVENTORY PREDICTIONS =====================

    /**
     * GET /api/analytics/inventory?date=2026-05-29
     * Fetch inventory waste predictions for a specific date.
     */
    @GetMapping("/inventory")
    public ResponseEntity<List<InventoryPrediction>> getInventoryPredictionsByDate(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date) {
        return ResponseEntity.ok(analyticsService.getInventoryPredictionsByDate(date));
    }

    /**
     * GET /api/analytics/inventory/range?startDate=2026-05-01&endDate=2026-05-31
     * Fetch inventory waste predictions within a date range.
     */
    @GetMapping("/inventory/range")
    public ResponseEntity<List<InventoryPrediction>> getInventoryPredictionsByDateRange(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate) {
        return ResponseEntity.ok(analyticsService.getInventoryPredictionsByDateRange(startDate, endDate));
    }

    /**
     * GET /api/analytics/inventory/action?action=Reduce Reorder Level
     * Fetch inventory predictions filtered by recommended action.
     */
    @GetMapping("/inventory/action")
    public ResponseEntity<List<InventoryPrediction>> getInventoryPredictionsByAction(
            @RequestParam String action) {
        return ResponseEntity.ok(analyticsService.getInventoryPredictionsByAction(action));
    }
}
