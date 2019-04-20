'use strict'

import React from 'react'
import axios from 'axios'
import { Input, Table, Icon, message, Popconfirm, Divider } from 'antd'
import { EditableCell, EditableFormRow, EditableContext } from '../../components/Form/UserForm'
import { DNSDialog } from "../../components/Dialog"


const { Search } = Input

export default class RoleManager extends React.Component {
  constructor(props) {
    super(props)
    this.state = { editVisible:false, editing_id: '', loading: true}
    this.total = 0
    this.limit = 10
    this.page = 1
    this.role = {}
    this.roles = []
    this.qs = undefined
    this.columns = [
      {title: '角色名', width: '30%', align: 'center', dataIndex: 'username', editable: false, key: 'username'},
      {title: '级别', width: '10%', align: 'center', dataIndex: 'sex', editable: true, key: 'sex',render: text => (
        text === 0? (
          <span>会员</span>
        ): (
         <span>管理员</span>
        )
      )},
      {title: '权限设置', width: '20%', align: 'center', dataIndex: 'permission', editable: true, key: 'permission'},
      {title: '操作', width: '20%', align: 'center', dataIndex: '_add', key: '_add',
        render: (text, record) => (
          this.isEditing(record) ? (
            <span>
              <EditableContext.Consumer>
                {form => (
                  <a
                    href='javascript:void(0)'
                    onClick={() => this.save(form, record._id)}
                    style={{ marginRight: 8 }}
                  >
                    保存
                  </a>
                )}
              </EditableContext.Consumer>
              <a
                href="javascript:;"
                onClick={() => this.cancel(record._id)}
                style={{ marginRight: 8 }}
              >
                取消
              </a>
            </span>
          ) : (
            <div>
              <a onClick={() => this.edit(record._id)}><Icon type='edit'  /></a>
              <Divider type='vertical'/>
              <Popconfirm title="确定删除?" onConfirm={() => this.delete(record._id)}>
                <a href="javascript:void(0)" > <Icon type='delete' /></a>
              </Popconfirm>
            </div>
          )
        )},
  ]
    this.intervalId = null
  }

  getRole = async () => {
    let params = {
      skip: (this.page - 1) * this.limit,
      limit: this.limit,
    }
    if (this.qs) {
      params.q = this.qs
    }
    await axios.get('/api/v1/roles', {params})
      .then(resp => {
        this.total = resp.data.total
        this.roles = resp.data.roles
      })
      .catch(e => {
        message.error('加载roles列表失败！')
      })
  }

  async componentDidMount() {
    const reloadroles = async () => {
      await this.getRole();
      this.setState({loading: false});
      this.intervalId = setTimeout(reloadroles, 10000) // reload tasks every 10 seconds
    };
    await reloadroles()
  }

  componentWillUnmount() {
    if (this.intervalId) {
      clearTimeout(this.intervalId)
    }
  }

  isEditing = record => record._id === this.state.editing_id

  cancel = () => {
    this.setState({ editing_id: '' })
  }

  handleChange = async role => {
    // edit
    await axios.put('/api/v1/role', role)
      .then(resp => {
        message.success('成功修改')
      })
      .catch(err => {
        message.error(`修改role失败，错误：${err}`)
      })
  }

  handleDelete = async (_id) => {
    // delete
    const url = '/api/v1/role?_id=' + _id;
    await axios.delete(url)
      .then(resp => {
        message.success('成功删除role配置')
      })
      .catch(err => {
        message.error(`删除role错误：${err}`)
      })
  }

  save = (form, _id) => {
    form.validateFields((error, row) => {
      if (error) {
        return
      }
      const newData = [...this.roles]
      const index = newData.findIndex(item => _id === item._id)
      const item = newData[index]
        newData.splice(index, 1, {
          ...item,
          ...row,
        })
      if (_id.length > 1) {
        this.handleChange(newData[index])
        this.getRole().then(() =>{
                this.setState({ editing_id: '' })
              })
      }
    })
  }

  edit = _id => {
    this.setState({ editing_id: _id })
  }

  delete = _id => {
    const dataSource = this.roles
    this.roles = dataSource.filter(item => item._id !== _id)
    this.handleDelete(_id)
    this.getRole().then(() =>{
                this.setState({ editing_id: '' })
              })
  }

  add = () =>{
    this.setState({editVisible: true})
  }

  handleSearch = async (e) => {
    this.qs = e || undefined
    this.setState({loading: true})
    await this.getRole()
    this.setState({loading: false})
  }

  render() {
    const components = {
      body: {
        row: EditableFormRow,
        cell: EditableCell,
      },
    };

    const columns = this.columns.map((col) => {

      if (!col.editable) {
        return col;
      }
      return {
        ...col,
        onCell: record => ({
          record,
          inputType: col.dataIndex === 'nettype' ? 'select' : 'text',
          dataIndex: col.dataIndex,
          title: col.title,
          editing: this.isEditing(record),
        }),
      };
    });

    const {loading} = this.state

    return (
      <div>
        <Table
          components={components}
          loading={loading}
          columns={columns}
          dataSource={this.roles}
          size='middle'
          rowKey='_id'
          pagination={{
            total: this.total,
            pageSize: this.limit,
            current: this.page,
            showTotal: total => `共 ${this.total} 个roles记录`,
            onChange: async (page, pageSize) => {
              this.page = page,
                this.total = pageSize,
                await this.getRole(),
                this.setState({loading: false})
            }
          }}
        />
        <DNSDialog
          dns={this.role}
          visible={this.state.editVisible}
          onSubmit={
            () => {
              this.getRole().then(async () => {
                this.setState({editVisible: false})
                await this.getRole(),
                this.setState({loading: false})
              })
            }
          }
          onClose={
            () => {
              this.role = null
              this.setState({editVisible: false})
            }
          }
        />
      </div>
    )
  }}
