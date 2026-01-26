# Java Refactoring Examples

This file contains comprehensive before/after examples moved from SKILL.md to keep the main file under 350 lines.

## Example 1: Refactor Legacy Data Access Code

**Before:**
```java
public class UserDAO {
    public User getUserById(int id) {
        Connection conn = null;
        PreparedStatement stmt = null;
        ResultSet rs = null;
        User user = null;

        try {
            conn = DriverManager.getConnection(DB_URL, USER, PASS);
            stmt = conn.prepareStatement("SELECT * FROM users WHERE id = ?");
            stmt.setInt(1, id);
            rs = stmt.executeQuery();

            if (rs.next()) {
                user = new User();
                user.setId(rs.getInt("id"));
                user.setName(rs.getString("name"));
                user.setEmail(rs.getString("email"));
            }
        } catch (SQLException e) {
            e.printStackTrace();
        } finally {
            try {
                if (rs != null) rs.close();
                if (stmt != null) stmt.close();
                if (conn != null) conn.close();
            } catch (SQLException e) {
                e.printStackTrace();
            }
        }

        return user;
    }
}
```

**After:**
```java
@Repository
@RequiredArgsConstructor
@Slf4j
public class UserRepository {
    private final JdbcTemplate jdbcTemplate;

    private static final RowMapper<User> USER_ROW_MAPPER = (rs, rowNum) ->
        User.builder()
            .id(rs.getInt("id"))
            .name(rs.getString("name"))
            .email(rs.getString("email"))
            .build();

    public Optional<User> findById(int id) {
        log.debug("Finding user by id: {}", id);
        try {
            User user = jdbcTemplate.queryForObject(
                "SELECT * FROM users WHERE id = ?",
                USER_ROW_MAPPER,
                id
            );
            return Optional.ofNullable(user);
        } catch (EmptyResultDataAccessException e) {
            log.debug("User not found with id: {}", id);
            return Optional.empty();
        } catch (DataAccessException e) {
            log.error("Database error while fetching user: id={}", id, e);
            throw new UserRepositoryException(
                "Failed to fetch user with id: " + id, e);
        }
    }
}
```

## Example 2: Refactor Procedural Service Logic

See original SKILL.md lines 617-780 for complete example.

## Example 3: Refactor Complex Conditionals

See original SKILL.md lines 782-888 for complete example.
