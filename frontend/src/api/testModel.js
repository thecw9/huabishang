import axios from "@/utils/testModelRequest";

export function getTestModelInfo(include, exclude = null) {
  const params = {
    include: include,
    exclude: exclude,
  };

  return axios.post("/info", params, {
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
  });
}

export function predictTestModel(name) {
  const data = {
    name: name,
  };
  return axios.post("/predict", data, {
    headers: {
      Accept: "application/json",
      "Content-Type": "application/json",
    },
  });
}
