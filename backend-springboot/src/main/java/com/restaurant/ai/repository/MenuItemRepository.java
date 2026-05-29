package com.restaurant.ai.repository;

import com.restaurant.ai.model.MenuItem;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

/**
 * Spring Data JPA Repository for MenuItem entities.
 */
@Repository
public interface MenuItemRepository extends JpaRepository<MenuItem, Integer> {

    /**
     * Find all currently available menu items.
     */
    List<MenuItem> findByIsAvailableTrue();

    /**
     * Find menu items by category.
     */
    List<MenuItem> findByCategory(String category);

    /**
     * Find a menu item by its name and category.
     */
    Optional<MenuItem> findByItemNameAndCategory(String itemName, String category);
}
