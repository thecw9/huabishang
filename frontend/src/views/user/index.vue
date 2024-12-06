<script setup>
import { ref, onMounted } from "vue";
import { ElMessageBox, ElNotification } from "element-plus";
import {
  getUserList,
  searchUser,
  deleteUser,
  addUser,
  updateUser,
} from "@/api/auth";

const addUserDialogVisible = ref(false);
const editUserDialogVisible = ref(false);
const background = ref(true);

const input = ref("");
const users = ref([]);
const currentPage = ref(1);
const pageSize = ref(10);
const total = ref(0);

const addForm = ref({
  username: "",
  email: "",
  password: "",
  privilege: 0,
});

const editForm = ref({
  id: "",
  username: "",
  password: "",
  email: "",
  privilege: 0,
});

const handleClose = () => {
  ElMessageBox.confirm("确认关闭？")
    .then(() => {
      addUserDialogVisible.value = false;
    })
    .catch(() => {});
};

// get user list
const setUserListData = async () => {
  const res = await getUserList(currentPage.value, pageSize.value);
  users.value = res.data.map((item) => {
    return {
      id: item.id,
      username: item.username,
      password: item.password,
      email: item.email,
      privilege: item.privilege,
      created_at: item.created_at.replace("T", " ").split(".")[0],
      updated_at: item.updated_at.replace("T", " ").split(".")[0],
    };
  });
  total.value = res.total;
};

onMounted(() => {
  setUserListData();
});

const handleCurrentChange = (val) => {
  currentPage.value = val;
  setUserListData();
};

// search user
const searchUserData = async () => {
  currentPage.value = 1;
  const res = await searchUser(input.value, currentPage.value, pageSize.value);
  users.value = res.data.map((item) => {
    return {
      id: item.id,
      username: item.username,
      email: item.email,
      is_active: item.is_active ? "是" : "否",
      is_superuser: item.is_superuser ? "是" : "否",
      created_at: item.created_at,
      updated_at: item.updated_at,
    };
  });
  total.value = res.data.data.total;
};

// delete user
const handleDelete = (id) => {
  ElMessageBox.confirm("确认删除？")
    .then(async () => {
      const res = await deleteUser(id);
      if (res.code === 200) {
        setUserListData();
        ElNotification({
          title: "成功",
          message: "删除成功",
          type: "success",
        });
        setUserListData();
      }
    })
    .catch(() => {});
};

// add user
const handleAddUser = async () => {
  const res = await addUser(addForm.value);
  if (res.code === 200) {
    ElNotification({
      title: "成功",
      message: "添加成功",
      type: "success",
    });
    setUserListData();
  }
  addUserDialogVisible.value = false;
};

//

// edit user
const rowToEditForm = (row) => {
  editForm.value = {
    id: row.id,
    username: row.username,
    email: row.email,
    privilege: row.privilege,
  };
  editUserDialogVisible.value = true;
};

const handleEditUser = async () => {
  console.log(editForm);
  const res = await updateUser(editForm.value.id, editForm.value);
  if (res.code === 200) {
    ElNotification({
      title: "成功",
      message: "编辑成功",
      type: "success",
    });
    setUserListData();
  }
  editUserDialogVisible.value = false;
};
</script>

<template>
  <div>
    <!-- 新增用户弹窗 -->
    <el-dialog
      v-model="addUserDialogVisible"
      title="新增用户"
      width="30%"
      :before-close="handleClose"
    >
      <el-form label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="addForm.username" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="addForm.email" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="addForm.password" />
        </el-form-item>
        <el-form-item label="权限">
          <el-input v-model="addForm.privilege" />
        </el-form-item>
      </el-form>
      <template #footer>
        <span class="dialog-footer">
          <el-button class="cancel-btn" @click="addUserDialogVisible = false"
            >Cancel</el-button
          >
          <el-button type="primary" @click="handleAddUser"> Confirm </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 编辑用户弹窗 -->
    <el-dialog
      v-model="editUserDialogVisible"
      title="编辑用户"
      width="30%"
      :before-close="handleClose"
    >
      <el-form label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="editForm.username" />
        </el-form-item>
        <el-form-item label="邮箱">
          <el-input v-model="editForm.email" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="editForm.password" />
        </el-form-item>
        <el-form-item label="权限">
          <el-input v-model="editForm.privilege" />
        </el-form-item>
      </el-form>

      <template #footer>
        <span class="dialog-footer">
          <el-button class="cancel-btn" @click="editUserDialogVisible = false"
            >Cancel</el-button
          >
          <el-button type="primary" @click="handleEditUser">
            Confirm
          </el-button>
        </span>
      </template>
    </el-dialog>

    <!-- 新增用户按钮和搜索框 -->
    <div class="input_box">
      <el-button type="primary" @click="addUserDialogVisible = true"
        >添加用户</el-button
      >
      <div>
        <el-input v-model="input" placeholder="请输入关键字" />
        <el-button type="primary" @click="searchUserData"> 搜索 </el-button>
        <el-button type="primary" @click="setUserListData"> 重置 </el-button>
      </div>
    </div>

    <!-- 用户列表 -->
    <div class="table-box">
      <el-table :data="users" border style="width: 100%">
        <el-table-column prop="username" label="用户名" />
        <el-table-column prop="email" label="邮箱" />
        <el-table-column prop="privilege" label="权限" />
        <el-table-column prop="created_at" label="创建时间" />
        <el-table-column prop="updated_at" label="更新时间" />
        <el-table-column label="操作" width="160">
          <template #default="{ row }">
            <el-button type="primary" @click="rowToEditForm(row)"
              >编辑</el-button
            >
            <el-button type="danger" @click="handleDelete(row.id)"
              >删除</el-button
            >
          </template>
        </el-table-column>
      </el-table>

      <!-- 分页 -->
      <div class="pagination">
        <el-pagination
          :background="background"
          :total="total"
          v-model:current-page="currentPage"
          v-model:page-size="pageSize"
          :page-sizes="[10, 20, 30, 50]"
          layout="prev, pager, next, sizes"
          @current-change="handleCurrentChange"
        />
      </div>
    </div>
  </div>
</template>

<style scoped>
.el-input {
  width: 300px;
  margin-right: 15px;
}
</style>
