package com.restaurant.ai.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * DTO representing a single item within an order request.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class OrderItemRequestDTO {

    /**
     * The ID of the menu item being ordered.
     */
    private Integer menuItemId;

    /**
     * The quantity of this menu item.
     */
    private Integer quantity;
}
