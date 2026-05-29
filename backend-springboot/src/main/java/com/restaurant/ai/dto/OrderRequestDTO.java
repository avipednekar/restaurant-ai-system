package com.restaurant.ai.dto;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/**
 * DTO representing the full incoming order request from the POS / frontend.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class OrderRequestDTO {

    /**
     * Payment method: Cash, Online, Credit Card, Gift Card.
     */
    private String paymentMethod;

    /**
     * Purchase type: In-store, Online, Drive-thru.
     */
    private String purchaseType;

    /**
     * ID of the cashier processing this order (optional).
     */
    private Integer cashierId;

    /**
     * City where the order is placed (optional).
     */
    private String city;

    /**
     * List of items being ordered.
     */
    private List<OrderItemRequestDTO> items;
}
