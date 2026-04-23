# Database Migration Automation

## Overview
Database migrations are automated on every deployment using Alembic. The migration runs before the application starts, ensuring schema is always in sync.

## How It Works

### Development
```bash
cd backend/services/auth-service

# Create new migration
uv run alembic revision --autogenerate -m "Add users table"

# Review generated migration in alembic/versions/
# Edit if needed to ensure correctness

# Run migrations locally
uv run alembic upgrade head

# Check migration status
uv run alembic current
```

### Docker/Kubernetes
Migrations run automatically via entrypoint script:
1. Container starts
2. Entrypoint script waits for DB connection
3. Alembic runs `upgrade head`
4. Application starts only after migrations complete

## Structure
```
service-name/
  alembic/
    versions/          # Migration scripts
    env.py            # Alembic environment config
  alembic.ini         # Alembic configuration
  main.py
```

## Best Practices

1. **Always test migrations locally first**
   ```bash
   docker-compose down -v  # Reset local DB
   docker-compose up       # Run migrations via container
   ```

2. **Write reversible migrations**
   ```python
   def upgrade():
       op.create_table('users', ...)

   def downgrade():
       op.drop_table('users')
   ```

3. **Keep migrations small and focused**
   - One logical change per migration
   - Easier to review and troubleshoot

4. **Test rollback scenarios**
   ```bash
   uv run alembic downgrade -1  # Rollback one version
   uv run alembic upgrade head   # Reapply
   ```

5. **Document complex migrations**
   Add comments in migration file explaining why the change is needed

## Migration Status

Check current migration version:
```bash
# Local
uv run alembic current

# Docker
docker-compose exec auth-service uv run alembic current

# Kubernetes
kubectl exec -it auth-service-xxxx -n taskscheduler -- uv run alembic current
```

List all migrations:
```bash
uv run alembic history
```

## Troubleshooting

### Migration fails on deploy
1. Check logs:
   ```bash
   kubectl logs deployment/auth-service -n taskscheduler
   ```

2. Check migration status:
   ```bash
   kubectl exec postgres-0 -n taskscheduler -- psql -U postgres -d taskscheduler -c "SELECT * FROM alembic_version;"
   ```

3. Manually fix if needed:
   ```bash
   kubectl exec postgres-0 -n taskscheduler -- psql -U postgres -d taskscheduler \
     -c "DELETE FROM alembic_version WHERE version_num = 'bad_migration_id';"
   ```

### Diverged migrations
If local and main branch have conflicting migrations:
```bash
# Reset and merge migrations
git merge main
uv run alembic merge heads -m "Merge migration branches"
```

## Reverting a Deployment

If migration causes issues:
```bash
# Stop rollout
kubectl rollout undo deployment/auth-service -n taskscheduler

# This also reverts DB to previous version (if migrations are reversible)
```

## CI/CD Integration
Migrations are tested in CI before merging:
```yaml
# In backend-ci.yaml
- name: Test migrations
  run: |
    cd backend/services/auth-service
    # Use test DB
    alembic upgrade head
```

## Production Safety
1. **Dry-run**: Always test migrations on staging first
2. **Backup**: Always backup production DB before deploy
3. **Monitoring**: Watch DB performance during migration
4. **Timing**: Schedule during low-traffic windows for large data migrations
