package com.restaurant.ai.repository;

import com.restaurant.ai.model.Order;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.stereotype.Repository;

import java.time.LocalDate;
import java.util.List;
import java.util.Optional;

/**
 * Spring Data JPA Repository for Order entities.
 * Uses JOIN FETCH to eagerly load orderItems in a single query, avoiding N+1.
 */
@Repository
public interface OrderRepository extends JpaRepository<Order, Integer> {

    /**
     * Fetch all orders with their items in a single query.
     */
    @Query("SELECT DISTINCT o FROM Order o LEFT JOIN FETCH o.orderItems oi LEFT JOIN FETCH oi.menuItem")
    List<Order> findAllWithItems();

    /**
     * Find a specific order by ID with items eagerly loaded.
     */
    @Query("SELECT o FROM Order o LEFT JOIN FETCH o.orderItems oi LEFT JOIN FETCH oi.menuItem WHERE o.id = :id")
    Optional<Order> findByIdWithItems(Integer id);

    /**
     * Find all orders placed on a specific date with items.
     */
    @Query("SELECT DISTINCT o FROM Order o LEFT JOIN FETCH o.orderItems oi LEFT JOIN FETCH oi.menuItem WHERE o.orderDate = :orderDate")
    List<Order> findByOrderDateWithItems(LocalDate orderDate);

    /**
     * Find all orders within a date range with items.
     */
    @Query("SELECT DISTINCT o FROM Order o LEFT JOIN FETCH o.orderItems oi LEFT JOIN FETCH oi.menuItem WHERE o.orderDate BETWEEN :startDate AND :endDate")
    List<Order> findByOrderDateBetweenWithItems(LocalDate startDate, LocalDate endDate);

    /**
     * Find orders by payment method.
     */
    List<Order> findByPaymentMethod(String paymentMethod);
}
