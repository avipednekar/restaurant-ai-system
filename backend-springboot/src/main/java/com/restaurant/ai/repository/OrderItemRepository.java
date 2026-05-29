package com.restaurant.ai.repository;

import com.restaurant.ai.model.OrderItem;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * Spring Data JPA Repository for OrderItem entities.
 */
@Repository
public interface OrderItemRepository extends JpaRepository<OrderItem, Integer> {

    /**
     * Find all items belonging to a specific order.
     */
    List<OrderItem> findByOrderId(Integer orderId);
}
