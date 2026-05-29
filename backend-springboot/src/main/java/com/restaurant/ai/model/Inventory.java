package com.restaurant.ai.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.time.LocalDateTime;

/**
 * JPA Entity mapped to the 'inventory' table.
 * Represents a daily snapshot of an inventory ingredient's stock level.
 */
@Entity
@Table(name = "inventory")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class Inventory {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(name = "item_id")
    private Integer itemId;

    @Column(name = "item_name", nullable = false, length = 100)
    private String itemName;

    @Column(nullable = false, length = 50)
    private String category;

    @Column(length = 50)
    private String subcategory;

    @Column(nullable = false, length = 20)
    private String unit;

    @Column(name = "current_stock", nullable = false, precision = 10, scale = 2)
    private BigDecimal currentStock = BigDecimal.ZERO;

    @Column(name = "reorder_level", nullable = false, precision = 10, scale = 2)
    private BigDecimal reorderLevel = BigDecimal.ZERO;

    @Column(name = "daily_usage", precision = 10, scale = 2)
    private BigDecimal dailyUsage = BigDecimal.ZERO;

    @Column(name = "lead_time_days")
    private Integer leadTimeDays = 1;

    @Column(name = "price_per_unit", precision = 10, scale = 2)
    private BigDecimal pricePerUnit = BigDecimal.ZERO;

    @Column(name = "supplier_name", length = 100)
    private String supplierName;

    @Column(name = "seasonal_factor", precision = 4, scale = 2)
    private BigDecimal seasonalFactor = BigDecimal.ONE;

    @Column(name = "waste_pct", precision = 5, scale = 2)
    private BigDecimal wastePct = BigDecimal.ZERO;

    @Column(name = "record_date", nullable = false)
    private LocalDate recordDate;

    @Column(name = "created_at", updatable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}
