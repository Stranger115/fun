'use strict'

import React from 'react'
import axios from 'axios'
import { Input, Table, Icon, message, Popconfirm, Divider } from 'antd'
import { ProductForm,LabelForm } from "../../components/Form"
import Modal from "antd/lib/modal";


const { Search } = Input

export default class ProdcutsManager extends React.Component {
  constructor(props) {
    super(props)
    this.state = {visibleLabel: false, visibleProduct:false, editing_id: '', loading: true}
    this.total = 0
    this.limit = 10
    this.page = 1
    this.product = {}
    this.products = []
    this.qs = undefined
    this.name = null
    this.columns = [
      {title: '名称', width: '20%', align: 'center', dataIndex: 'name', editable: true, key: 'name',
        render: (text, record) =>(
          <span>
            <span>{text}&nbsp; &nbsp;</span>
            <a onClick={() => this.handleEdit(record)}><Icon  type="edit" /></a>
            <Divider type='vertical'/>
            <a onClick={() => this.handleDelete(record.name)}><Icon type="delete" /></a>
          </span>
        )},
      {title: '库存', width: '20%', align: 'center', dataIndex: 'stock', editable: true, key: 'stock'},
      {title: '价格', width: '20%', align: 'center', dataIndex: 'price', editable: true, key: 'price'},
      {title: (
          <span>
            <span>种类</span>
            <a onClick={this.handleAddLabel}><Icon  type="plus" /></a>
          </span>
        ), width: '20%', align: 'center', dataIndex: 'label', editable: true, key: 'label'},
      {
        title: (
          <span>
            <a href='javascript:void(0)' onClick={this.handleAddProduct}><Icon type='plus' /></a>
            <Search
              placeholder='输入名称进行筛选'
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
         record.flag?(
           <span>
             <span>上架</span>
             <Divider type='vertical'/>
             <span>
               <a onClick={() => this.handUpdateState(false, record.name)}>
                 下架
               </a>
             </span>
           </span>
         ):(
           <span>
             <span><a onClick={() =>  this.handUpdateState(true, record.name)}>
                 上架
               </a>
             </span>
             <Divider type='vertical'/>
             <span>下架</span>
           </span>
         )
        )},
  ]
    this.intervalId = null
  }

  getProduct = async () => {
    let params = {
      skip: (this.page - 1) * this.limit,
      limit: this.limit,
    }
    await axios.get('/api/v1/all_products', )
      .then(resp => {
        this.total = resp.data.total
        this.products = resp.data.products
      })
      .catch(e => {
        message.error('加载prodcut列表失败！')
      })
  }

  async componentDidMount() {
    const reloadproduct = async () => {
      await this.getProduct();
      this.setState({loading: false});
      this.intervalId = setTimeout(reloadproduct, 10000) // reload tasks every 10 seconds
    };
    await reloadproduct()
  }

  componentWillUnmount() {
    if (this.intervalId) {
      clearTimeout(this.intervalId)
    }
  }

  handUpdateState = async (flag, name) => {
    flag = {'flag': flag, 'name':name}
    await axios.get('/api/v1/all_products', flag)
      .then(resp => {
        if (flag){
          message.success('上架成功！')
        }
        else{
          message.success('下架成功！')
        }
      })
      .catch(e => {
        if (flag){
          message.error('上架失败！')
        }
        else{
          message.error('下架失败！')
        }
      })
    await this.getProduct()
  }

  handleChange = async product => {
    // edit
    await axios.put('/api/v1/product', product)
      .then(resp => {
        message.success('成功修改')
      })
      .catch(err => {
        message.error(`修改prodcut失败，错误：${err}`)
      })
    await this.getProduct()
  }

  handleDelete = async (name) => {
    // delete
    let value = {'name':name}
    await axios.delete('/api/v1/product', value)
      .then(resp => {
        message.success('成功删除商品')
      })
      .catch(err => {
        message.error(`删除商品错误：${err}`)
      })
    await this.getProduct()
  }
  handleEdit = async (record) =>{
    this.handleAddProduct()
    this.product = record
  }

  handleAddProduct = () =>{
    this.setState({visibleProduct:true})
  }
  handleCloseProduct =() =>{
    this.setState({visibleProduct:false})
  }

  handleSubmitProduct = async ()=>{
    this.handleCloseProduct()
    await this.getProduct()
  }

  handleAddLabel = () =>{
    this.setState({visibleLabel:true})
  }
  handleCloseLabel =() =>{
    this.setState({visibleLabel:false})
  }

  handleSearch = async (e) => {
    this.qs = e || undefined
    this.setState({loading: true})
    await this.getprodcut()
    this.setState({loading: false})
  }

  render() {
    const columns = this.columns.map((col) => {
      return {
        ...col,
        onCell: record => ({
          record,
          inputType: col.dataIndex === 'text',
          dataIndex: col.dataIndex,
          title: col.title,
        }),
      };
    });

    const {loading} = this.state

    return (
      <div>
        <Table
          loading={loading}
          columns={columns}
          dataSource={this.products}
          size='middle'
          rowKey='_id'
          pagination={{
            total: this.total,
            pageSize: this.limit,
            current: this.page,
            showTotal: total => `共 ${this.total} 个prodcut记录`,
            onChange: async (page, pageSize) => {
              this.page = page,
                this.total = pageSize,
                await this.getProduct(),
                this.setState({loading: false})
            }
          }}
        />
        <Modal
          title="添加商品"
          width={340}
          visible={this.state.visibleProduct}
          onCancel={this.handleCloseProduct}
          footer={null}
        >
          <ProductForm product={this.product} onSubmit={this.handleSubmitProduct}/>
        </Modal>
        <Modal
          title="添加分类"
          width={340}
          visible={this.state.visibleLabel}
          onCancel={this.handleCloseLabel}
          footer={null}>
          <LabelForm onSubmit={this.handleCloseLabel}/>
        </Modal>
      </div>
    )
  }}



