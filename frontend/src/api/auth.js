import axios from "@/utils/authRequest";

export function login(username, password) {
  const data =
    "grant_type=password&username=" +
    username +
    "&password=" +
    password +
    "&scope=&client_id=&client_secret=";

  return axios.post("/access_token", data, {
    headers: {
      Accept: "application/json",
      "Content-Type": "application/x-www-form-urlencoded",
    },
  });
}

export function getUserList(page, size) {
  return axios.get("/users/", {
    params: {
      page: page,
      limit: size,
    },
    headers: {
      accept: "application/json",
    },
  });
}

export function searchUser(keyword, page, size) {
  return axios.get("/users/search/", {
    params: {
      username: keyword,
      page: page,
      limit: size,
    },
    headers: {
      accept: "application/json",
    },
  });
}

export function deleteUser(id) {
  return axios.delete("/users/" + id, {
    headers: {
      accept: "application/json",
    },
  });
}

export function addUser(data) {
  return axios.post("/users/", data, {
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
  });
}

export function updateUser(id, data) {
  return axios.put("/users/" + id, data, {
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
  });
}
