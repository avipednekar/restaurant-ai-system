package com.restaurant.ai.controller;

import com.restaurant.ai.model.MenuItem;
import com.restaurant.ai.service.MenuService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/**
 * REST Controller for menu item operations.
 * Used by the POS frontend to display available dishes.
 */
@RestController
@RequestMapping("/api/menu")
@RequiredArgsConstructor
public class MenuController {

    private final MenuService menuService;

    /**
     * GET /api/menu
     * Fetches all available menu items for the POS screen.
     */
    @GetMapping
    public ResponseEntity<List<MenuItem>> getAvailableMenuItems() {
        List<MenuItem> items = menuService.getAvailableMenuItems();
        return ResponseEntity.ok(items);
    }

    /**
     * GET /api/menu/all
     * Fetches all menu items including unavailable ones (admin view).
     */
    @GetMapping("/all")
    public ResponseEntity<List<MenuItem>> getAllMenuItems() {
        List<MenuItem> items = menuService.getAllMenuItems();
        return ResponseEntity.ok(items);
    }

    /**
     * GET /api/menu/category/{category}
     * Fetches menu items filtered by category.
     */
    @GetMapping("/category/{category}")
    public ResponseEntity<List<MenuItem>> getMenuItemsByCategory(@PathVariable String category) {
        List<MenuItem> items = menuService.getMenuItemsByCategory(category);
        return ResponseEntity.ok(items);
    }

    /**
     * GET /api/menu/{id}
     * Fetches a specific menu item by its ID.
     */
    @GetMapping("/{id}")
    public ResponseEntity<MenuItem> getMenuItemById(@PathVariable Integer id) {
        return menuService.getMenuItemById(id)
                .map(ResponseEntity::ok)
                .orElse(ResponseEntity.notFound().build());
    }
}
