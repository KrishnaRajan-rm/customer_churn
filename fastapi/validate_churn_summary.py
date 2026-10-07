import sys
sys.path.insert(0, '.')
import fastapi.main as main
app = main.app
routes = [r for r in app.routes if getattr(r, 'path', None) == '/churn/summary']
print('route_count=', len(routes))
print('route_exists=', bool(routes))
print('response_model=', routes[0].response_model.__name__ if routes else 'MISSING')
