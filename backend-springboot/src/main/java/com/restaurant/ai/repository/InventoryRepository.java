package com.restaurant.ai.repository;

import com.restaurant.ai.model.Inventory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * Spring Data JPA Repository for Inventory entities.
 */
@Repository
public interface InventoryRepository extends JpaRepository<Inventory, Integer> {

    /**
     * Find the most recent inventory record for a specific item by name.
     */
    Optional<Inventory> findTopByItemNameOrderByRecordDateDesc(String itemName);

    /**
     * Find all inventory records for a specific item.
     */
    List<Inventory> findByItemName(String itemName);
}
