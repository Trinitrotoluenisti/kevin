# Kevin API v0.1

## #0.X Authentication

### #0.1 /login POST

_Make the login process with the given credentials_

#### Headers


#### Body

- **username:** `<string>`
- **password:** `<string>`


#### Responses

- **Status code:** 200
- **msg:** Ok
- **access_token:** `<string>`
- **refresh_token:** `<string>`

### #0.2 /register POST

_Create a new user and add it into the database_

#### Headers


#### Body

- **username:** `<string>`
- **email:** `<string>`
- **password:** `<string>`


#### Responses

- **Status code:** 200
- **msg:** Ok
- **access_token:** `<string>`
- **refresh_token:** `<string>`

### #0.3 /refresh POST

_Generate a new access token from refresh token_

#### Headers

- **Authorization:** Bearer: `<refresh_token>`

#### Body



#### Responses

- **Status code:** 200
- **msg:** Ok
- **access_token:** `<STRING>`

## #1.X Users

### #1.0.1 /user GET

_Returns your informations_

#### Headers

- **Authorization:** Bearer: `<access_token>`

#### Body



#### Responses

- **Status code:** 200
- **msg:** Ok
- **username:** `<STRING>`
- **email:** `<STRING>`
- **perms:** `<INTEGER>`

### #1.0.2 /user/`<USERNAME>` GET

_Returns informations about the given username_

#### Headers


#### Body



#### Responses

- **Status code:** 200
- **msg:** Ok
- **username:** `<STRING>`
- **perms:** `<INTEGER>`

_auto-generated docs_
