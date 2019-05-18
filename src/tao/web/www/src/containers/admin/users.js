'use strict'

import React from 'react'
import axios from 'axios'
import { Input, Table, Icon, message, Popconfirm, Divider } from 'antd'
import { EditableCell, EditableFormRow, EditableContext } from '../../components/Form/UserForm'
import { DNSDialog } from "../../components/Dialog"
import {LabelForm, RoleForm, UserForm} from "../../components/Form";
import Modal from "antd/lib/modal";


const { Search } = Input

export default class UserManager extends React.Component {
  constructor(props) {
    super(props)
    this.state = { visibleRole:false, editVisible:false, editing_id: '', loading: true}
    this.total = 0
    this.limit = 10
    this.page = 1
    this.user = {}
    this.users = []
    this.qs = undefined
    this.columns = [
      {title: '昵称', width: '30%', align: 'center', dataIndex: 'username', editable: false, key: 'username'},
      {title: '性别', width: '10%', align: 'center', dataIndex: 'sex', editable: true, key: 'sex',render: text => (
        text === 1? (
          <div>
            <Icon type="woman" />
          </div>
        ): (
          <div>
            <Icon type="man" />
          </div>
        )
      )},
      {title: '电话', width: '20%', align: 'center', dataIndex: 'role', editable: true, key: 'role'},
      {title:(
          <span>
            <span>会员等级</span>
            <a onClick={this.handleAddRole}><Icon  type="plus" /></a>
          </span>
        ), width: '20%', align: 'center', dataIndex: 'role', editable: true, key: 'role'},
      {
        title: (
          <span>
            <a href='javascript:void(0)' onClick={this.add}><Icon type='plus' /></a>
            <Search
              placeholder='输入昵称，会员等级进行筛选'
              onSearch={this.handleSearch}
              onChange={e => {
                if (e.target.value==='') {
                  this.handleSearch('')
                }
              }}
              allowClear={true}
              style={{width: '80%', marginLeft: '10%'}}
            />
          </span>
        ),
        width: '20%',
        align: 'center',
        dataIndex: '_add',
        key: '_add',
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

  getUser = async () => {
    let params = {
      skip: (this.page - 1) * this.limit,
      limit: this.limit,
    }
    if (this.qs) {
      params.q = this.qs
    }
    await axios.get('/api/v1/users', {params})
      .then(resp => {
        this.total = resp.data.total
        this.users = resp.data.users
      })
      .catch(e => {
        message.error('加载users列表失败！')
      })
  }

  async componentDidMount() {
    const reloadusers = async () => {
      await this.getUser();
      this.setState({loading: false});
      this.intervalId = setTimeout(reloadusers, 10000) // reload tasks every 10 seconds
    };
    await reloadusers()
  }

  componentWillUnmount() {
    if (this.intervalId) {
      clearTimeout(this.intervalId)
    }
  }

  isEditing = record => record._id === this.state.editing_id

  handleAddRole = () =>{
    this.setState({visibleRole:true})
  }

  handleCloseRole = () =>{
    this.setState({visibleRole:false})
  }

  cancel = () => {
    this.setState({ editing_id: '' })
  }

  handleChange = async user => {
    // edit
    await axios.put('/api/v1/user', user)
      .then(resp => {
        message.success('成功修改')
      })
      .catch(err => {
        message.error(`修改user失败，错误：${err}`)
      })
  }

  handleDelete = async (_id) => {
    // delete
    const url = '/api/v1/user?_id=' + _id;
    await axios.delete(url)
      .then(resp => {
        message.success('成功删除user配置')
      })
      .catch(err => {
        message.error(`删除user错误：${err}`)
      })
  }

  save = (form, _id) => {
    form.validateFields((error, row) => {
      if (error) {
        return
      }
      const newData = [...this.users]
      const index = newData.findIndex(item => _id === item._id)
      const item = newData[index]
        newData.splice(index, 1, {
          ...item,
          ...row,
        })
      if (_id.length > 1) {
        this.handleChange(newData[index])
        this.getUser().then(() =>{
                this.setState({ editing_id: '' })
              })
      }
    })
  }

  edit = _id => {
    this.setState({ editing_id: _id })
  }

  delete = _id => {
    const dataSource = this.users
    this.users = dataSource.filter(item => item._id !== _id)
    this.handleDelete(_id)
    this.getUser().then(() =>{
                this.setState({ editing_id: '' })
              })
  }

  add = () =>{
    this.setState({editVisible: true})
  }

  handleSearch = async (e) => {
    this.qs = e || undefined
    this.setState({loading: true})
    await this.getUser()
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
          dataSource={this.users}
          size='middle'
          rowKey='_id'
          pagination={{
            total: this.total,
            pageSize: this.limit,
            current: this.page,
            showTotal: total => `共 ${this.total} 个users记录`,
            onChange: async (page, pageSize) => {
              this.page = page,
                this.total = pageSize,
                await this.getUser(),
                this.setState({loading: false})
            }
          }}
        />
        <DNSDialog
          dns={this.user}
          visible={this.state.editVisible}
          onSubmit={
            () => {
              this.getUser().then(async () => {
                this.setState({editVisible: false})
                await this.getUser(),
                this.setState({loading: false})
              })
            }
          }
          onClose={
            () => {
              this.user = null
              this.setState({editVisible: false})
            }
          }
        />
        <Modal
          title="添加会员等级"
          width={340}
          visible={this.state.visibleRole}
          onCancel={this.handleCloseRole}
          footer={null}>
          <LabelForm onSubmit={this.handleCloseRole}/>
        </Modal>
      </div>

    )
  }}



