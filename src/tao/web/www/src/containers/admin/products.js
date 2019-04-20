'use strict'

import React from 'react'
import axios from 'axios'
import { Input, Table, Icon, message, Popconfirm, Divider } from 'antd'
import { EditableCell, EditableFormRow, EditableContext } from '../../components/Form/DNSForm'
import { DNSDialog } from "../../components/Dialog"


const { Search } = Input

export default class ProdcutsManager extends React.Component {
  constructor(props) {
    super(props)
    this.state = { editVisible:false, editing_id: '', loading: true}
    this.total = 0
    this.limit = 10
    this.page = 1
    this.dns = {}
    this.DNS = []
    this.qs = undefined
    this.columns = [
      {title: 'FQDN', width: '30%', align: 'center', dataIndex: 'fqdn', editable: true, key: 'fqdn'},
      {title: 'IP', width: '20%', align: 'center', dataIndex: 'ip', editable: true, key: 'ip'},
      {title: '网络类型', width: '20%', align: 'center', dataIndex: 'nettype', editable: true, key: 'nettype', render: text => (
        text === 'intranet'? (
          <div>
            <Icon type="home" />内网IP
          </div>
        ): (
          <div>
            <Icon type="ie" />外网IP
          </div>
        )
      )},
      {
        title: (
          <span>
            <a href='javascript:void(0)' onClick={this.add}><Icon type='plus' /></a>
            <Search
              placeholder='输入FQDN、IP进行筛选'
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

  getDNS = async () => {
    let params = {
      skip: (this.page - 1) * this.limit,
      limit: this.limit,
    }
    if (this.qs) {
      params.q = this.qs
    }
    await axios.get('/api/v1/dns', {params})
      .then(resp => {
        this.total = resp.data.total
        this.DNS = resp.data.dns
      })
      .catch(e => {
        message.error('加载DNS列表失败！')
      })
  }

  async componentDidMount() {
    const reloaddns = async () => {
      await this.getDNS();
      this.setState({loading: false});
      this.intervalId = setTimeout(reloaddns, 10000) // reload tasks every 10 seconds
    };
    await reloaddns()
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

  handleChange = async dns => {
    // edit
    await axios.put('/api/v1/dns', dns)
      .then(resp => {
        message.success('成功修改')
      })
      .catch(err => {
        message.error(`修改dns失败，错误：${err}`)
      })
  }

  handleDelete = async (_id) => {
    // delete
    const url = '/api/v1/dns?_id=' + _id;
    await axios.delete(url)
      .then(resp => {
        message.success('成功删除DNS配置')
      })
      .catch(err => {
        message.error(`删除DNS错误：${err}`)
      })
  }

  save = (form, _id) => {
    form.validateFields((error, row) => {
      if (error) {
        return
      }
      const newData = [...this.DNS]
      const index = newData.findIndex(item => _id === item._id)
      const item = newData[index]
        newData.splice(index, 1, {
          ...item,
          ...row,
        })
      if (_id.length > 1) {
        this.handleChange(newData[index])
        this.getDNS().then(() =>{
                this.setState({ editing_id: '' })
              })
      }
    })
  }

  edit = _id => {
    this.setState({ editing_id: _id })
  }

  delete = _id => {
    const dataSource = this.DNS
    this.DNS = dataSource.filter(item => item._id !== _id)
    this.handleDelete(_id)
    this.getDNS().then(() =>{
                this.setState({ editing_id: '' })
              })
  }

  add = () =>{
    this.setState({editVisible: true})
  }

  handleSearch = async (e) => {
    this.qs = e || undefined
    this.setState({loading: true})
    await this.getDNS()
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
          dataSource={this.DNS}
          size='middle'
          rowKey='_id'
          pagination={{
            total: this.total,
            pageSize: this.limit,
            current: this.page,
            showTotal: total => `共 ${this.total} 个DNS记录`,
            onChange: async (page, pageSize) => {
              this.page = page,
                this.total = pageSize,
                await this.getDNS(),
                this.setState({loading: false})
            }
          }}
        />
        <DNSDialog
          dns={this.dns}
          visible={this.state.editVisible}
          onSubmit={
            () => {
              this.getDNS().then(async () => {
                this.setState({editVisible: false})
                await this.getDNS(),
                this.setState({loading: false})
              })
            }
          }
          onClose={
            () => {
              this.dns = null
              this.setState({editVisible: false})
            }
          }
        />
      </div>
    )
  }}



