package pcy.study.aiplayground.repository;

import org.springframework.data.jpa.repository.JpaRepository;
import pcy.study.aiplayground.entity.Product;

public interface ProductRepository extends JpaRepository<Product, Long> {
}
