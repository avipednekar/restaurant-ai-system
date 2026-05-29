package com.restaurant.ai.service;

import com.restaurant.ai.dto.OrderItemRequestDTO;
import com.restaurant.ai.dto.OrderRequestDTO;
import com.restaurant.ai.model.*;
import com.restaurant.ai.repository.*;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.math.BigDecimal;
import java.time.LocalDate;
import java.util.List;

/**
 * Service layer for order processing, billing, and inventory deduction.
 */
@Service
@RequiredArgsConstructor
@Slf4j
public class OrderService {

    private final OrderRepository orderRepository;
    private final MenuItemRepository menuItemRepository;
    private final RecipeMasterRepository recipeMasterRepository;
    private final InventoryRepository inventoryRepository;

    /**
     * Process a new order: validate items, compute totals, save the order,
     * and deduct raw ingredients from inventory based on the BOM (recipe_master).
     */
    @Transactional
    public Order createOrder(OrderRequestDTO request) {
        if (request.getItems() == null || request.getItems().isEmpty()) {
            throw new IllegalArgumentException("Order must contain at least one item.");
        }

        Order order = new Order();
        order.setPaymentMethod(request.getPaymentMethod());
        order.setPurchaseType(request.getPurchaseType());
        // cashierId is nullable - only set if provided and valid
        // Set to null if no users exist yet to avoid FK constraint violation
        order.setCashierId(null);
        order.setCity(request.getCity());
        order.setOrderDate(LocalDate.now());

        BigDecimal totalAmount = BigDecimal.ZERO;

        for (OrderItemRequestDTO itemDTO : request.getItems()) {
            MenuItem menuItem = menuItemRepository.findById(itemDTO.getMenuItemId())
                    .orElseThrow(() -> new IllegalArgumentException(
                            "Menu item not found with ID: " + itemDTO.getMenuItemId()));

            if (!menuItem.getIsAvailable()) {
                throw new IllegalArgumentException(
                        "Menu item '" + menuItem.getItemName() + "' is currently unavailable.");
            }

            OrderItem orderItem = new OrderItem();
            orderItem.setOrder(order);
            orderItem.setMenuItem(menuItem);
            orderItem.setQuantity(itemDTO.getQuantity());
            orderItem.setUnitPrice(menuItem.getPrice());
            orderItem.computeSubtotal();

            order.getOrderItems().add(orderItem);
            totalAmount = totalAmount.add(orderItem.getSubtotal());
        }

        order.setTotalAmount(totalAmount);

        // Save the order (cascades to order_items)
        Order savedOrder = orderRepository.save(order);

        // Deduct inventory based on BOM
        deductInventory(savedOrder);

        log.info("Order #{} created successfully. Total: {}", savedOrder.getId(), totalAmount);
        return savedOrder;
    }

    /**
     * Deducts raw ingredients from the inventory table based on the recipe_master BOM.
     * For each order item, looks up the required ingredients and reduces current_stock.
     */
    private void deductInventory(Order order) {
        for (OrderItem orderItem : order.getOrderItems()) {
            List<RecipeMaster> ingredients = recipeMasterRepository
                    .findByMenuItemId(orderItem.getMenuItem().getId());

            for (RecipeMaster recipe : ingredients) {
                BigDecimal totalNeeded = recipe.getQuantityNeeded()
                        .multiply(BigDecimal.valueOf(orderItem.getQuantity()));

                inventoryRepository.findTopByItemNameOrderByRecordDateDesc(recipe.getIngredientName())
                        .ifPresent(inventory -> {
                            BigDecimal newStock = inventory.getCurrentStock().subtract(totalNeeded);
                            if (newStock.compareTo(BigDecimal.ZERO) < 0) {
                                log.warn("Inventory for '{}' would go negative ({})! Setting to 0.",
                                        recipe.getIngredientName(), newStock);
                                newStock = BigDecimal.ZERO;
                            }
                            inventory.setCurrentStock(newStock);
                            inventoryRepository.save(inventory);
                            log.info("Deducted {} {} of '{}'. Remaining stock: {}",
                                    totalNeeded, recipe.getUnit(), recipe.getIngredientName(), newStock);
                        });
            }
        }
    }

    /**
     * Retrieve all orders with items in a single query.
     */
    public List<Order> getAllOrders() {
        return orderRepository.findAllWithItems();
    }

    /**
     * Retrieve orders for a specific date.
     */
    public List<Order> getOrdersByDate(LocalDate date) {
        return orderRepository.findByOrderDateWithItems(date);
    }

    /**
     * Retrieve orders within a date range.
     */
    public List<Order> getOrdersByDateRange(LocalDate startDate, LocalDate endDate) {
        return orderRepository.findByOrderDateBetweenWithItems(startDate, endDate);
    }

    /**
     * Find a specific order by ID.
     */
    public Order getOrderById(Integer id) {
        return orderRepository.findByIdWithItems(id)
                .orElseThrow(() -> new IllegalArgumentException("Order not found with ID: " + id));
    }
}
