export function trimNumber(number, decimalPlaces = 4) {
  // check if the input is a number
  if (typeof number !== "number") {
    return number;
  }

  let roundedNumber = number.toFixed(decimalPlaces); // 保留指定的小数位数
  let trimmedNumber = parseFloat(roundedNumber); // 将字符串转换为数字，去除末尾的零

  return trimmedNumber.toString(); // 返回格式化后的数字字符串
}

export function mergeArrays(arr1, arr2, key) {
  return arr1.map((item1) => {
    let item2 = arr2.find((item2) => item2[key] === item1[key]);

    return {
      ...item1,
      ...item2,
    };
  });
}

export function formatDate(date) {
  // 将时间转化为中国时区的格式
  let options = {
    timeZone: "Asia/Shanghai",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    second: "2-digit",
    fractionalSecondDigits: 3, // 设置毫秒部分显示三位数字
  };

  // 将时间格式化为字符串
  let formattedDate = new Intl.DateTimeFormat("zh-CN", options).format(date);

  // 将字符串转换为期望的格式
  formattedDate = formattedDate
    .replace(/\//g, "-")
    .replace(" ", "T")
    .replace(":", ":");
  return formattedDate;
}

export function alarmCodeToStatus(alarmCode) {
  switch (alarmCode) {
    case -1:
      return "-1";
    case 0:
      return "正常";
    case 1:
      return "注意";
    case 2:
      return "警告";
    case 3:
      return "严重";
    case 4:
      return "紧急";
    default:
      return "未知";
  }
}

export const tableRowClassName = ({ row }) => {
  if (row.status === "正常") {
    return "success-row";
  } else if (row.status === "注意") {
    return "watch-row";
  } else if (row.status === "警告") {
    return "warning-row";
  } else if (row.status === "严重") {
    return "critical-row";
  } else if (row.status === "紧急") {
    return "emergency-row";
  } else {
    return "unknown-row";
  }
};

export const formatText = (text) => {
  if (!text) return "";
  // return description;
  return text.replace(/\n/g, "<br>");
};
