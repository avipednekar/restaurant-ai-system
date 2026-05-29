package com.restaurant.ai.model;

import jakarta.persistence.*;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.math.BigDecimal;

/**
 * JPA Entity mapped to the 'recipe_master' table.
 * Represents a Bill of Materials (BOM) entry linking a menu item
 * to the raw ingredients needed to prepare it.
 */
@Entity
@Table(name = "recipe_master")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class RecipeMaster {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @ManyToOne(fetch = FetchType.LAZY)
    @JoinColumn(name = "menu_item_id", nullable = false)
    private MenuItem menuItem;

    @Column(name = "ingredient_name", nullable = false, length = 100)
    private String ingredientName;

    @Column(name = "quantity_needed", nullable = false, precision = 10, scale = 3)
    private BigDecimal quantityNeeded;

    @Column(nullable = false, length = 20)
    private String unit;

    @Column(name = "ingredient_category", length = 50)
    private String ingredientCategory;
}
