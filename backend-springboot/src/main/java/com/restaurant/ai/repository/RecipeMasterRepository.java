package com.restaurant.ai.repository;

import com.restaurant.ai.model.RecipeMaster;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

/**
 * Spring Data JPA Repository for RecipeMaster (BOM) entities.
 */
@Repository
public interface RecipeMasterRepository extends JpaRepository<RecipeMaster, Integer> {

    /**
     * Find all ingredient entries for a specific menu item.
     * Used during order processing to determine which inventory items to deduct.
     */
    List<RecipeMaster> findByMenuItemId(Integer menuItemId);
}
