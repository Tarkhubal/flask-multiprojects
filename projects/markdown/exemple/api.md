# Documentation API

## endpoints disponibles

### GET /

retourne la page d'accueil

**réponse :**
```json
{
    "status": "ok",
    "message": "bienvenue"
}
```

### GET /users

récupère la liste des utilisateurs

**paramètres :**
- `page` (int) : numéro de page (défaut: 1)
- `limit` (int) : nombre de résultats (défaut: 10)

**exemple :**
```bash
curl http://localhost:5000/users?page=1&limit=5
```

**réponse :**
```json
{
    "users": [
        {"id": 1, "name": "john"},
        {"id": 2, "name": "jane"}
    ],
    "total": 42,
    "page": 1
}
```

### POST /users

crée un nouvel utilisateur

**corps de la requête :**
```json
{
    "name": "nouveau utilisateur",
    "email": "user@exemple.com"
}
```

**réponse :**
```json
{
    "id": 3,
    "name": "nouveau utilisateur",
    "created": "2025-10-15T12:00:00Z"
}
```

### PUT /users/:id

met à jour un utilisateur

**paramètres :**
- `id` (int) : identifiant utilisateur

**corps de la requête :**
```json
{
    "name": "nom modifié"
}
```

### DELETE /users/:id

supprime un utilisateur

**paramètres :**
- `id` (int) : identifiant utilisateur

**réponse :**
```json
{
    "status": "deleted"
}
```

## codes d'erreur

| code | description |
|------|-------------|
| 200  | succès |
| 201  | créé |
| 400  | requête invalide |
| 401  | non autorisé |
| 404  | non trouvé |
| 500  | erreur serveur |

## authentification

utiliser un token bearer dans les headers :

```bash
curl -H "Authorization: Bearer votre-token" http://localhost:5000/users
```

[← guide installation](installation.md) | [retour accueil](index.md)
