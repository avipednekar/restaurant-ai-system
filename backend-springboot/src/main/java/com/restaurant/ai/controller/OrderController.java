package com.restaurant.ai.controller;

import com.restaurant.ai.dto.OrderRequestDTO;
import com.restaurant.ai.model.Order;
import com.restaurant.ai.service.OrderService;
import lombok.RequiredArgsConstructor;
import org.springframework.format.annotation.DateTimeFormat;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.time.LocalDate;
import java.util.List;
import java.util.Map;

/**
 * REST Controller for order (billing) operations.
 * Handles creating new orders and retrieving order history.
 */
@RestController
@RequestMapping("/api/orders")
@RequiredArgsConstructor
public class OrderController {

    private final OrderService orderService;

    /**
     * POST /api/orders
     * Submit a new bill/order from the POS.
     * Automatically deducts inventory ingredients based on the BOM.
     *
     * Example payload:
     * {
     *   "paymentMethod": "Cash",
     *   "purchaseType": "In-store",
     *   "cashierId": 1,
     *   "items": [
     *     { "menuItemId": 1, "quantity": 2 },
     *     { "menuItemId": 5, "quantity": 1 }
     *   ]
     * }
     */
    @PostMapping
    public ResponseEntity<?> createOrder(@RequestBody OrderRequestDTO request) {
        try {
            Order savedOrder = orderService.createOrder(request);
            return ResponseEntity.status(HttpStatus.CREATED).body(Map.of(
                    "success", true,
                    "message", "Order created successfully",
                    "orderId", savedOrder.getId(),
                    "totalAmount", savedOrder.getTotalAmount()
            ));
        } catch (IllegalArgumentException e) {
            return ResponseEntity.badRequest().body(Map.of(
                    "success", false,
                    "error", e.getMessage()
            ));
        }
    }

    /**
     * GET /api/orders
     * Retrieve all orders (sales history).
     */
    @GetMapping
    public ResponseEntity<List<Order>> getAllOrders() {
        return ResponseEntity.ok(orderService.getAllOrders());
    }

    /**
     * GET /api/orders/{id}
     * Retrieve a specific order by its ID.
     */
    @GetMapping("/{id}")
    public ResponseEntity<?> getOrderById(@PathVariable Integer id) {
        try {
            Order order = orderService.getOrderById(id);
            return ResponseEntity.ok(order);
        } catch (IllegalArgumentException e) {
            return ResponseEntity.notFound().build();
        }
    }

    /**
     * GET /api/orders/date?date=2026-05-29
     * Retrieve orders for a specific date.
     */
    @GetMapping("/date")
    public ResponseEntity<List<Order>> getOrdersByDate(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate date) {
        return ResponseEntity.ok(orderService.getOrdersByDate(date));
    }

    /**
     * GET /api/orders/range?startDate=2026-05-01&endDate=2026-05-31
     * Retrieve orders within a date range.
     */
    @GetMapping("/range")
    public ResponseEntity<List<Order>> getOrdersByDateRange(
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate startDate,
            @RequestParam @DateTimeFormat(iso = DateTimeFormat.ISO.DATE) LocalDate endDate) {
        return ResponseEntity.ok(orderService.getOrdersByDateRange(startDate, endDate));
    }
}
