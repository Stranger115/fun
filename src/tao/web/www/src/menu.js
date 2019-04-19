import React from 'react'
import Tasks from './containers/tasks'
import TaskDetail from './containers/tasks/detail'
import Deploy from './containers/deploy'
import Feature from './containers/feature'
import FeatureDetail from './containers/feature/detail'
import Release from './containers/release'
import ReleaseDetail from './containers/release/detail'
import ProductsManager from './containers/products'
import ModulesManager from './containers/modules'
import EnvsManager from './containers/environments'
import DNSManager from './containers/dns'
import Store from './containers/store'
import Admin from './containers/admin'


export default [
  {
    name: '商品列表',
    url: '/store:id',
    icon: 'shopping-cart',
    component: Store,
    inMenu: true,
    role:0x00,
    subMenu:null,
  },
  {
    name: '管理模块',
    url: '/admin',
    icon: 'schedule',
    component: Admin,
    inMenu: true,
    role: 0,//0xff,
    subMenu:[
      {
        name: '会员管理',
        url: '/store:id',
        icon: 'shopping-cart',
        component: Store,
        inMenu: true,
        role:0x00,
      },
      {
        name: '商品管理',
        url: '/store:id',
        icon: 'shopping-cart',
        component: Store,
        inMenu: true,
        role:0x00,
      },
      {
        name: '账单管理',
        url: '/store:id',
        icon: 'shopping-cart',
        component: Store,
        inMenu: true,
        role:0x00,
      }
    ],
  }, {
    name: 'Featuree详情',
    url: '/feature/:id',
    component: FeatureDetail,
    inMenu: false,
  }, {
    name: 'Release看板',
    url: '/release',
    icon: 'tags',
    component: Release,
    inMenu: true,
  }, {
    name: 'Release详情',
    url: '/release/:id',
    component: ReleaseDetail,
    inMenu: false,
  }, {
    name: '应用部署',
    url: '/deploy',
    icon: 'appstore',
    component: Deploy,
    inMenu: true,
  }, {
    name: '任务队列',
    url: '/tasks',
    icon: 'bars',
    component: Tasks,
    inMenu: true,
  }, {
    name: '任务详情',
    url: '/tasks/:id',
    component: TaskDetail,
    inMenu: false,
  }, {
    name: '产品管理',
    url: '/products',
    icon: 'project',
    component: ProductsManager,
    inMenu: true,
  }, {
    name: '产品详情',
    url: '/products/:id',
    component: ProductsManager,
    inMenu: false,
  }, {
    name: '模块管理',
    url: '/components',
    icon: 'block',
    component: ModulesManager,
    inMenu: true,
  }, {
    name: '环境管理',
    url: '/environments',
    icon: 'database',
    component: EnvsManager,
    inMenu: true,
  }, {
    name: 'DNS管理',
    url: '/dns',
    icon: 'scan',
    component: DNSManager,
    inMenu: true,
  }
]
