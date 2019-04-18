'use strict'

import React from 'react'
import _ from 'lodash'
import { Steps, Tooltip, Row, Col, Divider, Icon, List } from 'antd'
import { PendingIcon, SuccessIcon, SkippedIcon, RunningIcon, FailedIcon } from '../../components/Icons'

const Status = {
  NEW: 'new',
  DEVELOP: 'develop',
  RELEASE: 'release',
  MERGED: 'merged',
  DONE: 'done',
  CLOSED: 'closed',
}

const getStatusIcon = status => {
  switch (status) {
    case 'success':
      return <SuccessIcon />
    case 'failed':
      return <FailedIcon />
    case 'skipped':
      return <SkippedIcon />
    case 'running':
      return <RunningIcon />
    case 'canceled':
      return <SkippedIcon />
    default:
      return <PendingIcon />
  }
}

const ComponentCI = ({item, pipeline}) => (
  <List.Item>
    <Row style={{width: '100%'}}>
      <Col span={8}><h4>{item.name}</h4></Col>
      <Col span={16}>
        <Divider type='vertical'/>
        {
          _(pipeline===undefined ? [] : pipeline.jobs)
            .sortBy('started_at')
            .reverse()
            .uniqBy('name')
            .reverse()
            .groupBy('stage')
            .map(group => (
              <span key={group[0].stage}>
                {
                  group.map(job => (
                    <Tooltip title={job.stage + ' / ' + job.name} key={job.name}>
                      <a target='_blank' href={job.web_url}>{getStatusIcon(job.status)}</a>
                    </Tooltip>
                  ))
                }
                <Divider type='vertical'/>
              </span>
            ))
            .value()
        }
      </Col>
    </Row>
  </List.Item>
)

export {
  Status,
  getStatusIcon,
  ComponentCI,
}
